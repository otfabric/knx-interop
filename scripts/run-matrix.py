#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run the knx-interop scenarios between every pair of adapters on an
isolated Docker bridge network, and write reports/<name>.json and .md.

Every scenario runs real implementations in containers; nothing is
simulated. A result is pass, fail, unsupported (an adapter or stack does not
offer the operation) or not-tested (a prerequisite failed).

The adapters are third-party stacks and the probe. A system under test
brings its own adapter image implementing the container contract
(--adapter NAME=IMAGE, for example go-knx's): it joins every role its
capabilities declare and is preferred as observer and responder.

Usage: run-matrix.py [--registry R] [--version V] [--adapter NAME=IMAGE ...] [--servers a,b] [--clients a,b]
                     [--suites tunnel,dpt,negative,routing,v2,secure] [--report NAME]

Writes reports/results.json (reports/<name>.results.json with --report), the
organisation's interop-result-v1. The run fails on a failure or infrastructure
error (with --gate, one that involves that adapter), on a waiver that no longer
reproduces, and when nothing passed.
"""

import argparse
import datetime
import fnmatch
import json
import os
import shlex
import subprocess
import sys
import threading
import time
import uuid

import interop_result

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVERS = ["knxd", "calimero-server"]
CLIENTS = ["xknx", "knxultimate", "calimero-tools", "knxd"]
ROUTERS = ["xknx", "knxultimate", "calimero-tools", "knxd"]
SERVER_NAME = "knx-interop"


def sh(args, timeout=120, check=False):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError("%s: %s" % (" ".join(args), p.stderr.strip() or p.stdout.strip()))
    return p


def load_known():
    known = []
    with open(os.path.join(ROOT, "tests", "known-differences.tsv")) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) != 8:
                raise SystemExit("tests/known-differences.tsv: want 8 columns: %r" % line)
            known.append(dict(zip(("id", "client", "peer", "scenario", "scope", "upstream_version", "evidence_url", "note"), f)))
    return known


def load_ids():
    ids = {}
    with open(os.path.join(ROOT, "scenarios", "ids.tsv")) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            suite, scenario, sid = line.rstrip("\n").split("\t")
            ids[(suite, scenario)] = sid
    return ids


# Scenarios that record the harness or its environment, not a stack.
INFRASTRUCTURE = {"server start", "secure server start", "negative suite"}


class Matrix:
    def __init__(self, a):
        self.a = a
        self.known = load_known()
        self.ids = load_ids()
        self.reproduced = {}  # waiver id -> did it reproduce, for waivers that ran
        self.server_container = None
        self.net = "knxi-" + uuid.uuid4().hex[:8]
        self.results = []
        self.caps = {}
        self.started = datetime.datetime.now(datetime.timezone.utc)

    def image(self, adapter):
        if adapter in self.a.external:
            return self.a.external[adapter]
        return "%s/knx-interop-%s:%s" % (self.a.registry, adapter, self.a.version)

    # -- containers --------------------------------------------------
    def capabilities(self, adapter):
        if adapter not in self.caps:
            p = sh(["docker", "run", "--rm", self.image(adapter), "capabilities"])
            try:
                self.caps[adapter] = json.loads(p.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                self.caps[adapter] = {"implementation": adapter, "version": "unknown", "features": {}}
        return self.caps[adapter]

    def start_server(self, adapter, routing=False, secure=False, tool_access=False):
        name = "knxi-srv-%s-%s" % (adapter, uuid.uuid4().hex[:6])
        args = ["docker", "run", "-d", "--name", name, "--network", self.net, self.image(adapter), "server", "--name", SERVER_NAME]
        if routing:
            args.append("--routing")
        if tool_access:
            args.append("--tool-access")
        if secure:
            args.append("--secure")
        sh(args, check=True)
        ip = sh(["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name], check=True).stdout.strip()
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            r = self.client("probe", "describe", ["--target", ip, "--timeout", "2"])
            if r["status"] == "pass":
                return name, ip
            time.sleep(1)
        logs = sh(["docker", "logs", "--tail", "30", name]).stdout + sh(["docker", "logs", "--tail", "30", name]).stderr
        self.stop(name)
        raise RuntimeError("server %s did not answer within 90 s: %s" % (adapter, logs[-1500:]))

    def stop(self, name):
        sh(["docker", "rm", "-f", name])

    def client(self, adapter, op, args, timeout=90):
        cmd = ["docker", "run", "--rm", "--network", self.net, self.image(adapter), "client", op] + args
        try:
            p = sh(cmd, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "fail", "error": "adapter timed out after %ds" % timeout, "data": {}}
        return parse_doc(p)

    def background(self, adapter, op, args, ready_timeout=30):
        """Start a long-running client operation (monitor, answer); return a
        handle once the adapter printed READY."""
        name = "knxi-bg-%s" % uuid.uuid4().hex[:8]
        cmd = ["docker", "run", "--rm", "--name", name, "--network", self.net, self.image(adapter), "client", op] + args
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ready = threading.Event()
        err = []

        def pump():
            for line in p.stderr:
                err.append(line)
                if line.strip() == "READY":
                    ready.set()
            ready.set()

        t = threading.Thread(target=pump, daemon=True)
        t.start()
        ok = ready.wait(ready_timeout)
        time.sleep(0.3)
        return {"proc": p, "name": name, "ready": ok and p.poll() is None, "stderr": err}

    def collect(self, h, timeout=60):
        try:
            out, _ = h["proc"].communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            sh(["docker", "rm", "-f", h["name"]])
            return {"status": "fail", "error": "timed out", "data": {}}
        doc = parse_out(out)
        if doc is None:
            return {"status": "fail", "error": "no result document: %s" % ("".join(h["stderr"])[-800:]), "data": {}}
        return doc

    # -- recording ---------------------------------------------------
    def record(self, suite, scenario, client, peer, status, start, error=None, data=None, observer=None):
        sid = self.ids.get((suite, scenario))
        if sid is None:
            raise SystemExit("scenario %r of suite %r has no ID: add it to scenarios/ids.tsv" % (scenario, suite))
        waiver = None
        for k in self.known:
            if fnmatch.fnmatch(client, k["client"]) and fnmatch.fnmatch(peer, k["peer"]) and fnmatch.fnmatch(scenario, k["scenario"]):
                if status == "fail":
                    status, error, waiver = "known-difference", "%s (observed: %s)" % (k["note"], error), k["id"]
                    self.reproduced[k["id"]] = True
                elif status == "pass":
                    self.reproduced.setdefault(k["id"], False)
                break
        r = {"id": sid, "suite": suite, "scenario": scenario, "client": client, "peer": peer, "status": status,
             "durationMs": int((time.monotonic() - start) * 1000)}
        if waiver:
            r["waiver"] = waiver
        for adapter, key in ((client, "clientVersion"), (peer, "peerVersion")):
            if adapter in self.caps:
                r[key] = self.caps[adapter].get("version")
        if observer:
            r["observer"] = observer
        if status == "fail" and self.server_container:
            # The server's side of a failure, for the analysis.
            p = sh(["docker", "logs", "--tail", "40", self.server_container])
            r["serverLog"] = (p.stdout + p.stderr)[-6000:]
        if error:
            r["error"] = error[:1500]
        if data:
            r["data"] = data
        self.results.append(r)
        mark = {"pass": "PASS", "fail": "FAIL", "unsupported": "UNSUP", "not-tested": "N/T", "known-difference": "KNOWN"}[status]
        print("%-5s %-8s %-32s %-15s -> %-15s %s" % (mark, suite, scenario, client, peer, (error or "")[:100]), flush=True)

    def feature(self, adapter, f):
        return self.capabilities(adapter).get("features", {}).get(f, False)

    # -- scenarios ---------------------------------------------------
    def observer_for(self, client):
        """A monitor of a client's telegrams: the system under test, else a
        secure-capable third-party stack (secure scenarios use it too)."""
        for o in list(self.a.external) + ["xknx", "calimero-tools"]:
            if o != client:
                return o
        return "xknx"

    def responder_for(self, client, secure=False):
        """A group read responder: the system under test, else xknx, else
        KNXUltimate; with secure, one that runs secure sessions. None when
        there is none."""
        for o in list(self.a.external) + ["xknx", "knxultimate"]:
            if o != client and self.feature(o, "answer") and (not secure or self.feature(o, "secure")):
                return o
        return None

    def tunnel_suite(self, server):
        """The tunnel, dpt and v2 scenarios of every client, each client
        against a fresh server: a tunnel a client leaves open (a peer that
        stops without disconnecting) holds one of the server's slots until
        it times out, and must not fail the clients after it."""
        for c in self.a.clients:
            self.capabilities(c)
            name, ip = self.start_server(server)
            self.server_container = name
            try:
                if "tunnel" in self.a.suites:
                    self.discover(c, server, ip)
                    self.describe(c, server, ip)
                    self.connect(c, server, ip)
                    self.write(c, server, ip)
                    self.read(c, server, ip)
                if "dpt" in self.a.suites:
                    self.dpt(c, server, ip)
                if "v2" in self.a.suites:
                    self.v2(c, server, ip)
            finally:
                self.server_container = None
                self.stop(name)
        if "negative" in self.a.suites:
            name, ip = self.start_server(server)
            self.server_container = name
            try:
                self.negative(server, ip)
            finally:
                self.server_container = None
                self.stop(name)

    def discover(self, c, server, ip):
        t = time.monotonic()
        if not self.feature(c, "discover"):
            return self.record("tunnel", "discover (multicast search)", c, server, "unsupported", t, self.capabilities(c).get("notes"))
        r = self.client(c, "discover", ["--timeout", "3"])
        if r["status"] != "pass":
            return self.record("tunnel", "discover (multicast search)", c, server, r["status"], t, r.get("error"))
        found = [d for d in r["data"].get("devices", []) if d.get("endpoint", "").split(":")[0] == ip]
        ok = bool(found) and SERVER_NAME in found[0].get("name", "")
        self.record("tunnel", "discover (multicast search)", c, server, "pass" if ok else "fail", t,
                    None if ok else "server %s not among %s" % (ip, r["data"].get("devices")), found[0] if found else None)

    def describe(self, c, server, ip):
        t = time.monotonic()
        if not self.feature(c, "describe"):
            return self.record("tunnel", "describe", c, server, "unsupported", t, self.capabilities(c).get("notes"))
        r = self.client(c, "describe", ["--target", ip])
        ok = r["status"] == "pass" and SERVER_NAME in str(r["data"].get("name", ""))
        status = r["status"] if r["status"] != "pass" else ("pass" if ok else "fail")
        self.record("tunnel", "describe", c, server, status, t, r.get("error") or (None if ok else "name %r" % r["data"].get("name")), r.get("data"))

    def connect(self, c, server, ip):
        t = time.monotonic()
        r = self.client(c, "connect", ["--target", ip])
        self.record("tunnel", "connect and disconnect", c, server, r["status"], t, r.get("error"), r.get("data"))

    def write(self, c, server, ip, vector=None, scenario="group write (DPT 1.001)", suite="tunnel", extra=None, obs_extra=None):
        v = vector or {"dpt": "1.001", "group": "1/0/1", "value": "on", "data": "01"}
        t = time.monotonic()
        o = self.observer_for(c)
        h = self.background(o, "monitor", ["--target", ip, "--count", "1", "--timeout", "15"] + (obs_extra or []))
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record(suite, scenario, c, server, "not-tested", t, "observer %s could not listen: %s" % (o, res.get("error")), observer=o)
        r = self.client(c, "write", ["--target", ip, "--group", v["group"], "--dpt", v["dpt"], "--value", v["value"], "--data", v["data"]] + (extra or []))
        obs = self.collect(h)
        if r["status"] != "pass":
            return self.record(suite, scenario, c, server, r["status"], t, r.get("error"), observer=o)
        seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == v["group"] and x.get("service") == "write"]
        if not seen:
            return self.record(suite, scenario, c, server, "fail", t, "observer %s saw no write to %s: %s" % (o, v["group"], obs.get("error") or obs.get("data")), observer=o)
        ok = seen[0].get("data", "").upper() == v["data"]
        self.record(suite, scenario, c, server, "pass" if ok else "fail", t,
                    None if ok else "observer %s saw %s, expected %s" % (o, seen[0].get("data"), v["data"]), {"seen": seen[0]}, observer=o)

    def read(self, c, server, ip, scenario="group read/response (DPT 9.001)", suite="tunnel", extra=None, resp_extra=None):
        t = time.monotonic()
        resp = self.responder_for(c, "--secure" in (resp_extra or []))
        if resp is None:
            return self.record(suite, scenario, c, server, "unsupported", t, "no responder for this client among the adapters")
        h = self.background(resp, "answer", ["--target", ip, "--group", "1/0/2", "--dpt", "9.001", "--value", "21.5", "--data", "0C33", "--count", "1", "--timeout", "20"] + (resp_extra or []))
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record(suite, scenario, c, server, "not-tested", t, "responder %s: %s" % (resp, res.get("error")), observer=resp)
        r = self.client(c, "read", ["--target", ip, "--group", "1/0/2", "--dpt", "9.001", "--timeout", "8"] + (extra or []))
        # Let the responder end by itself after its answer (--count 1): a
        # killed responder leaves its tunnel, and a secure user's bound
        # address, open on the server until it times out.
        if r["status"] == "pass":
            self.collect(h, 30)
        else:
            sh(["docker", "rm", "-f", h["name"]])
            h["proc"].wait(10)
        if r["status"] != "pass":
            return self.record(suite, scenario, c, server, r["status"], t, r.get("error"), observer=resp)
        d = r["data"]
        ok = d.get("data", "").upper() == "0C33" or str(d.get("value")).startswith("21.5")
        self.record(suite, scenario, c, server, "pass" if ok else "fail", t, None if ok else "response %r" % d, d, observer=resp)

    def server_feature(self, server, f):
        return (self.capabilities(server).get("features", {}).get("server") or {}).get(f, False)

    def v2(self, c, server, ip):
        """Contract 1.1: tunnelling over TCP, device management, busmonitor."""
        t = time.monotonic()
        if self.feature(c, "tcp") and self.server_feature(server, "tcp"):
            self.write(c, server, ip, None, "group write over TCP (DPT 1.001)", "v2", ["--tcp"])
            self.read(c, server, ip, "group read over TCP (DPT 9.001)", "v2", ["--tcp"])
        else:
            for sc in ("group write over TCP (DPT 1.001)", "group read over TCP (DPT 9.001)"):
                self.record("v2", sc, c, server, "unsupported", t, "no TCP on the %s" % ("client" if not self.feature(c, "tcp") else "server"))
        t = time.monotonic()
        sc = "device management: device serial number (M_PropRead)"
        if self.feature(c, "property") and self.server_feature(server, "property"):
            r = self.client(c, "property", ["--target", ip, "--object", "0", "--pid", "11"])
            data = r.get("data", {}).get("data", "")
            ok = r["status"] == "pass" and len(data) == 12
            self.record("v2", sc, c, server, r["status"] if r["status"] != "pass" else ("pass" if ok else "fail"), t,
                        r.get("error") or (None if ok else "serial %r" % data), r.get("data"))
        else:
            self.record("v2", sc, c, server, "unsupported", t, "no device management on the %s" % ("client" if not self.feature(c, "property") else "server"))
        t = time.monotonic()
        sc = "busmonitor sees a write (L_Busmon.ind, TP1 frame)"
        if not (self.feature(c, "busmonitor") and self.server_feature(server, "busmonitor")):
            return self.record("v2", sc, c, server, "unsupported", t, "no busmonitor on the %s" % ("client" if not self.feature(c, "busmonitor") else "server"))
        writer = self.observer_for(c)
        h = self.background(c, "busmonitor", ["--target", ip, "--count", "1", "--timeout", "15"])
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record("v2", sc, c, server, "not-tested" if res["status"] != "fail" else "fail", t, res.get("error"))
        w = self.client(writer, "write", ["--target", ip, "--group", "1/0/7", "--dpt", "1.001", "--value", "on", "--data", "01"])
        res = self.collect(h)
        if w["status"] != "pass":
            return self.record("v2", sc, c, server, "not-tested", t, "writer %s: %s" % (writer, w.get("error")), observer=writer)
        frames = res.get("data", {}).get("frames", [])
        ok = bool(frames) and frames[0].get("raw", "").upper()[6:10] == "0807"
        self.record("v2", sc, c, server, "pass" if ok else (res["status"] if res["status"] != "pass" else "fail"), t,
                    None if ok else "frames %s %s" % (frames, res.get("error") or ""), {"frames": frames[:1]}, observer=writer)

    # -- KNX Secure (contract 1.2) -------------------------------------
    def secure_suite(self):
        for server in self.a.servers:
            self.capabilities(server)
            t = time.monotonic()
            if not self.server_feature(server, "secure"):
                self.record("secure", "secure tunnelling server", "-", server, "unsupported", t, "no KNX IP Secure server")
                continue
            # A fresh secure server for each scenario: a peer stopped while
            # connected (Calimero tools' monitor) leaves its user's session,
            # and the bound tunnelling address, on Calimero server until it
            # times out.
            steps = []
            for c in self.a.clients:
                self.capabilities(c)
                if not self.feature(c, "secure"):
                    self.record("secure", "secure tunnelling", c, server, "unsupported", time.monotonic(), "no KNX IP Secure client")
                    continue
                steps += [(c, f) for f in self.secure_steps(c, server)]

            def refused(ip):
                t = time.monotonic()
                plain = self.observer_for(server)
                r = self.client(plain, "connect", ["--target", ip, "--tcp"])
                ok = r["status"] == "fail"
                self.record("secure", "plain connection refused by the secure server", plain, server, "pass" if ok else "fail", t,
                            None if ok else "a plain tunnel was accepted: %s" % r.get("data"))
            steps.append((None, refused))
            for c, f in steps:
                t = time.monotonic()
                try:
                    name, ip = self.start_server(server, secure=True)
                except RuntimeError as e:
                    self.record("secure", "secure server start", c or "-", server, "fail", t, str(e))
                    continue
                self.server_container = name
                try:
                    f(ip)
                finally:
                    self.server_container = None
                    self.stop(name)
        self.secure_routing()
        self.secure_server_routing()

    def secure_steps(self, c, server):
        """The secure tunnelling scenarios of client c, each a function of
        the server's address; unsupported ones are recorded at once."""
        user2, user3 = ["--secure", "--user", "2"], ["--secure", "--user", "3"]
        steps = []

        def connect(ip):
            t = time.monotonic()
            r = self.client(c, "connect", ["--target", ip] + user2)
            status, err = r["status"], r.get("error")
            if status == "pass" and r["data"].get("address") not in ("1.1.10", None, ""):
                status, err = "fail", "user 2 got %s, not its address 1.1.10" % r["data"].get("address")
            self.record("secure", "secure session connect (user 2, bound address)", c, server, status, t, err, r.get("data"))
        steps.append(connect)
        steps.append(lambda ip: self.write(c, server, ip, None, "secure tunnel group write (DPT 1.001)", "secure", user2, user3))
        steps.append(lambda ip: self.read(c, server, ip, "secure tunnel group read/response (DPT 9.001)", "secure", user2, user3))
        sc = "Data Secure group write through a secure tunnel (DPT 9.001)"
        if self.feature(c, "dataSecure") and self.feature(self.observer_for(c), "dataSecure"):
            v = {"dpt": "9.001", "group": "1/3/2", "value": "21.5", "data": "0C33"}
            steps.append(lambda ip, sc=sc: self.write(c, server, ip, v, sc, "secure", user2, user3))
        else:
            self.record("secure", sc, c, server, "unsupported", time.monotonic(), "no Data Secure")
        # Contract 1.3: the secure session over UDP.
        if self.feature(c, "secureUdp") and self.server_feature(server, "secureUdp"):
            udp2 = user2 + ["--udp"]

            def connect_udp(ip):
                t = time.monotonic()
                r = self.client(c, "connect", ["--target", ip] + udp2)
                self.record("secure", "secure session over UDP (user 2)", c, server, r["status"], t, r.get("error"), r.get("data"))
            steps.append(connect_udp)
            steps.append(lambda ip: self.write(c, server, ip, None, "secure group write over UDP (DPT 1.001)", "secure", udp2, user3))
            steps.append(lambda ip: self.read(c, server, ip, "secure group read/response over UDP (DPT 9.001)", "secure", udp2, user3))
        else:
            for sc in ("secure session over UDP (user 2)", "secure group write over UDP (DPT 1.001)", "secure group read/response over UDP (DPT 9.001)"):
                self.record("secure", sc, c, server, "unsupported", time.monotonic(),
                            "no secure sessions over UDP on the %s" % ("client" if not self.feature(c, "secureUdp") else "server"))
        sc = "secure device management: serial number (user 1)"
        if self.feature(c, "property") and self.server_feature(server, "property"):
            def devmgmt(ip, sc=sc):
                t = time.monotonic()
                r = self.client(c, "property", ["--target", ip, "--object", "0", "--pid", "11", "--secure", "--user", "1"])
                data = r.get("data", {}).get("data", "")
                ok = r["status"] == "pass" and len(data) == 12
                self.record("secure", sc, c, server, r["status"] if r["status"] != "pass" else ("pass" if ok else "fail"), t,
                            r.get("error") or (None if ok else "serial %r" % data), r.get("data"))
            steps.append(devmgmt)
        else:
            self.record("secure", sc, c, server, "unsupported", time.monotonic(), "no device management on the %s" % ("client" if not self.feature(c, "property") else "server"))
        return steps

    # -- remote device management (contract 1.4) ------------------------
    def management_suite(self):
        """The remote property services of the server's device (1.1.0)
        through a tunnel: plain, connectionless and in a transport
        connection; with --tool-access, secured with the device's tool key
        (KNX Data Secure point to point), and plain access refused. A fresh
        server for each client: the write changes the friendly name."""
        name_hex = SERVER_NAME.encode().hex().upper()
        name_args = ["--object", "11", "--pid", "76", "--start", "1", "--count", str(len(SERVER_NAME))]
        write_args = ["--object", "11", "--pid", "76", "--start", "1", "--count", "4", "--data", "746F6F6C"]
        plain = [
            ("remote property read: friendly name (A_PropertyValue_Read)", [], name_hex),
            ("remote property read in a transport connection", ["--connected"], name_hex),
            ("remote property write, then read back (A_PropertyValue_Write)", ["--connected", "write"], "746F6F6C"),
        ]
        secured = [
            ("tool access read: S-A_Sync, then S-A_Data (tool key)", ["--tool-access"], name_hex),
            ("tool access read in a transport connection", ["--tool-access", "--connected"], name_hex),
            ("tool access write (S-A_Data, tool key)", ["--tool-access", "write"], "746F6F6C"),
        ]
        refused = "plain management refused by a secured device"
        for server in self.a.servers:
            self.capabilities(server)
            if not self.server_feature(server, "remoteProperty"):
                self.record("management", "remote property services", "-", server, "unsupported", time.monotonic(), "no remote device management on the server")
                continue
            for c in self.a.clients:
                self.capabilities(c)
                if not self.feature(c, "remoteProperty"):
                    self.record("management", "remote property services", c, server, "unsupported", time.monotonic(), "no remote device management on the client")
                    continue
                self.management_run(c, server, plain, name_args, write_args, False)
                if not self.server_feature(server, "toolAccess"):
                    for sc, _, _ in secured + [(refused, None, None)]:
                        self.record("management", sc, c, server, "unsupported", time.monotonic(), "no tool key access on the server")
                    continue
                steps = secured if self.feature(c, "toolAccess") else []
                if not steps:
                    for sc, _, _ in secured:
                        self.record("management", sc, c, server, "unsupported", time.monotonic(), "no tool key access on the client")
                self.management_run(c, server, steps, name_args, write_args, True, refused)

    def management_run(self, c, server, steps, name_args, write_args, tool_access, refused=None):
        if not steps and not refused:
            return
        t = time.monotonic()
        try:
            name, ip = self.start_server(server, tool_access=tool_access)
        except RuntimeError as e:
            return self.record("management", "server start", c, server, "fail", t, str(e))
        self.server_container = name
        try:
            for sc, flags, want in steps:
                t = time.monotonic()
                args = ["--target", ip] + (write_args if "write" in flags else name_args) + [f for f in flags if f != "write"]
                r = self.client(c, "remote-property", args)
                data = r.get("data", {}).get("data", "")
                status, err = r["status"], r.get("error")
                if status == "pass" and data.upper() != want:
                    status, err = "fail", "data %r, want %r" % (data, want)
                self.record("management", sc, c, server, status, t, err, r.get("data"))
            if refused:
                # Plain access to the secured device: in a connection, which
                # every remote property client has.
                t = time.monotonic()
                r = self.client(c, "remote-property", ["--target", ip, "--connected", "--timeout", "3"] + name_args)
                status, err = r["status"], r.get("error")
                if status == "pass":
                    status, err = "fail", "plain access answered: %r" % r.get("data")
                elif status == "fail":
                    status, err = "pass", None
                self.record("management", refused, c, server, status, t, err)
        finally:
            self.server_container = None
            self.stop(name)

    def secure_routing(self):
        routers = [x for x in self.a.routers if self.feature(x, "secure")]
        for x in self.a.routers:
            if x not in routers:
                self.record("secure", "secure routing", x, "-", "unsupported", time.monotonic(), "no KNX IP Secure routing")
        cases = [("secure routing write (DPT 1.001)", {"group": "1/0/9", "dpt": "1.001", "value": "on", "data": "01"}, None),
                 ("Data Secure group write over secure routing (DPT 9.001)", {"group": "1/3/1", "dpt": "9.001", "value": "21.5", "data": "0C33"}, "dataSecure")]
        for w in routers:
            for m in routers:
                if w == m:
                    continue
                for scenario, v, need in cases:
                    t = time.monotonic()
                    if need == "dataSecure" and w == "calimero-tools" and self.feature(m, "surrogate"):
                        # Calimero tools send Data Secure through a surrogate
                        # device (the profile's 15.15.255, group 1/3/3); a
                        # monitor that is one serves it.
                        v = dict(v, group="1/3/3")
                    if need and not (self.feature(w, need) and self.feature(m, need)):
                        self.record("secure", scenario, w, m, "unsupported", t, "no Data Secure")
                        continue
                    h = self.background(m, "monitor", ["--routing", "--secure", "--count", "1", "--timeout", "20"], ready_timeout=40)
                    if not h["ready"]:
                        res = self.collect(h, 30)
                        self.record("secure", scenario, w, m, "not-tested", t, "monitor: %s" % res.get("error"))
                        continue
                    r = self.client(w, "write", ["--routing", "--secure", "--group", v["group"], "--dpt", v["dpt"], "--value", v["value"], "--data", v["data"]])
                    obs = self.collect(h)
                    if r["status"] != "pass":
                        self.record("secure", scenario, w, m, r["status"], t, r.get("error"))
                        continue
                    seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == v["group"]]
                    ok = bool(seen) and seen[0].get("data", "").upper() == v["data"]
                    self.record("secure", scenario, w, m, "pass" if ok else "fail", t,
                                None if ok else "monitor saw %s %s" % (obs.get("data"), obs.get("error") or ""))

    def secure_server_routing(self):
        """Contract 1.3: a server's secure routing, in from a secure router
        (seen by a secure tunnel client) and out from a secure tunnel
        client (seen by a secure router). Each case gets a fresh server
        (see secure_suite)."""
        routers = [x for x in self.a.routers if self.feature(x, "secure")]
        for server in self.a.servers:
            t = time.monotonic()
            if not self.server_feature(server, "secureRouting"):
                self.record("secure", "server secure routing", "-", server, "unsupported", t, "no secure routing in the server")
                continue
            for w in routers:
                if w != server:
                    self.with_routing_server(server, "secure routing into the server, seen by a secure tunnel", w,
                                             lambda ip, w=w: self.server_routing_in(server, ip, w))
            for m in routers:
                writer = next(x for x in list(self.a.external) + ["xknx", "calimero-tools"] if x != m and self.feature(x, "secure"))
                self.with_routing_server(server, "secure routing out of the server, from a secure tunnel", writer,
                                         lambda ip, m=m, writer=writer: self.server_routing_out(server, ip, m, writer))

    def with_routing_server(self, server, scenario, client, f):
        t = time.monotonic()
        try:
            name, ip = self.start_server(server, routing=True, secure=True)
        except RuntimeError as e:
            return self.record("secure", scenario, client, server, "fail", t, "server start: %s" % e)
        self.server_container = name
        time.sleep(4)  # the server's timer synchronisation
        try:
            f(ip)
        finally:
            self.server_container = None
            self.stop(name)

    def server_routing_in(self, server, ip, w):
        t = time.monotonic()
        sc = "secure routing into the server, seen by a secure tunnel"
        o = self.observer_for(w)
        h = self.background(o, "monitor", ["--target", ip, "--secure", "--user", "3", "--count", "1", "--timeout", "20"])
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record("secure", sc, w, server, "not-tested", t, "observer %s: %s" % (o, res.get("error")), observer=o)
        r = self.client(w, "write", ["--routing", "--secure", "--group", "1/0/9", "--dpt", "1.001", "--value", "on", "--data", "01"])
        obs = self.collect(h)
        if r["status"] != "pass":
            return self.record("secure", sc, w, server, r["status"], t, r.get("error"), observer=o)
        seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == "1/0/9"]
        ok = bool(seen) and seen[0].get("data", "").upper() == "01"
        self.record("secure", sc, w, server, "pass" if ok else "fail", t,
                    None if ok else "observer %s saw %s %s" % (o, obs.get("data"), obs.get("error") or ""), observer=o)

    def server_routing_out(self, server, ip, m, writer):
        t = time.monotonic()
        sc = "secure routing out of the server, from a secure tunnel"
        h = self.background(m, "monitor", ["--routing", "--secure", "--count", "1", "--timeout", "20"], ready_timeout=40)
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record("secure", sc, writer, server, "not-tested", t, "router %s: %s" % (m, res.get("error")), observer=m)
        r = self.client(writer, "write", ["--target", ip, "--secure", "--user", "2", "--group", "1/0/7", "--dpt", "1.001", "--value", "on", "--data", "01"])
        obs = self.collect(h)
        if r["status"] != "pass":
            return self.record("secure", sc, writer, server, r["status"], t, r.get("error"), observer=m)
        seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == "1/0/7"]
        ok = bool(seen) and seen[0].get("data", "").upper() == "01"
        self.record("secure", sc, writer, server, "pass" if ok else "fail", t,
                    None if ok else "router %s saw %s %s" % (m, obs.get("data"), obs.get("error") or ""), observer=m)

    def dpt(self, c, server, ip):
        vectors = json.load(open(os.path.join(ROOT, "fixtures", "dpt-vectors.json")))["vectors"]
        for v in vectors:
            self.write(c, server, ip, v, "DPT %s %s" % (v["dpt"], v["value"]), "dpt")

    def negative(self, server, ip):
        t = time.monotonic()
        r = self.client("probe", "negative", ["--target", ip], timeout=300)
        self.capabilities("probe")
        for chk in r.get("data", {}).get("checks", []):
            # "observed" checks record behaviour the standard leaves open.
            st = {"pass": "pass", "fail": "fail", "info": "pass"}[chk["status"]]
            detail = chk["detail"] if chk["kind"] == "required" else "observed: " + chk["detail"]
            self.record("negative", chk["name"], "probe", server, st, time.monotonic(), None if st == "pass" else detail,
                        {"detail": detail, "kind": chk["kind"]})
        if not r.get("data", {}).get("checks"):
            self.record("negative", "negative suite", "probe", server, "fail", t, r.get("error"))

    def routing_suite(self):
        for w in self.a.routers:
            for m in self.a.routers:
                if w == m:
                    continue
                self.capabilities(w)
                self.capabilities(m)
                t = time.monotonic()
                scenario = "routing write (multicast)"
                if not self.feature(w, "routing") or not self.feature(m, "routing"):
                    self.record("routing", scenario, w, m, "unsupported", t, "no routing")
                    continue
                h = self.background(m, "monitor", ["--routing", "--count", "1", "--timeout", "15"])
                if not h["ready"]:
                    res = self.collect(h, 30)
                    self.record("routing", scenario, w, m, "not-tested", t, "monitor: %s" % res.get("error"))
                    continue
                r = self.client(w, "write", ["--routing", "--group", "1/0/9", "--dpt", "1.001", "--value", "on", "--data", "01"])
                obs = self.collect(h)
                if r["status"] != "pass":
                    self.record("routing", scenario, w, m, r["status"], t, r.get("error"))
                    continue
                seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == "1/0/9"]
                ok = bool(seen) and seen[0].get("data", "").upper() == "01"
                self.record("routing", scenario, w, m, "pass" if ok else "fail", t, None if ok else "monitor saw %s" % obs.get("data") or obs.get("error"))

    # -- reports -----------------------------------------------------
    def report(self):
        os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
        summary = {}
        for r in self.results:
            summary[r["status"]] = summary.get(r["status"], 0) + 1
        doc = {"schemaVersion": "1.0", "startedAt": self.started.isoformat(), "finishedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "host": {"platform": sys.platform, "machine": os.uname().machine},
               "implementations": {k: {"implementation": v.get("implementation"), "version": v.get("version"), "roles": v.get("roles")} for k, v in sorted(self.caps.items())},
               "summary": summary, "results": self.results}
        base = os.path.join(ROOT, "reports", self.a.report)
        with open(base + ".json", "w") as f:
            json.dump(doc, f, indent=2, sort_keys=True)
            f.write("\n")
        with open(base + ".md", "w") as f:
            f.write(markdown(doc))
        print("\n%s\nreports: %s.json, %s.md" % (summary, base, base))
        results = self.result_document(doc["finishedAt"])
        path = os.path.join(ROOT, "reports", "results.json" if self.a.report == "latest" else self.a.report + ".results.json")
        interop_result.write(path, results)
        print("results: %s" % path)
        failed = [r for r in self.results if r["status"] == "fail"]
        problems = interop_result.problems(results)
        for p in problems:
            print("FAIL %s" % p)
        if failed and not problems:
            print("%d failures, none involving %s: reported, not gating" % (len(failed), self.a.gate))
        return not problems

    def result_document(self, finished):
        """The run as interop-result-v1. The status "fail" of a scenario that
        records the harness itself is the outcome "infra-error"."""
        results = []
        for r in self.results:
            outcome = "infra-error" if r["status"] == "fail" and r["scenario"] in INFRASTRUCTURE else r["status"]
            roles = {"client": r["client"], "peer": r["peer"]}
            if r.get("observer"):
                roles["observer"] = r["observer"]
            res = {"id": r["id"], "title": r["scenario"], "suite": r["suite"], "outcome": outcome, "durationMs": r["durationMs"],
                   "roles": {k: v for k, v in roles.items() if v != "-"}}
            if outcome != "pass":
                res["reason"] = r.get("error") or outcome
            if r.get("waiver"):
                res["waiver"] = r["waiver"]
            results.append(res)
        implementations = []
        for name, caps in sorted(self.caps.items()):
            i = {"name": name, "version": str(caps.get("version") or "unknown"), "independent": name not in self.a.external}
            if caps.get("implementation"):
                i["upstream"] = caps["implementation"]
            digest = interop_result.repo_digest(self.image(name))
            if digest:
                i["image"] = digest
            implementations.append(i)
        waivers = []
        for k in self.known:
            if k["id"] in self.reproduced:
                waivers.append({"id": k["id"], "scope": k["scope"], "evidence": k["evidence_url"], "reproduced": self.reproduced[k["id"]]})
        doc = {"schemaVersion": "1.0", "repository": "otfabric/knx-interop", "interopVersion": interop_result.version_field(ROOT, "interop_version"),
               "contractVersion": interop_result.version_field(ROOT, "contract_version"), "gitSha": interop_result.git_sha(ROOT),
               "startedAt": self.started.strftime("%Y-%m-%dT%H:%M:%SZ"), "finishedAt": finished, "host": interop_result.host(),
               "implementations": implementations or [{"name": "none", "version": "none"}], "waivers": waivers,
               "reproduce": "python3 " + shlex.join(["scripts/run-matrix.py"] + sys.argv[1:]), "results": results}
        if self.a.gate:
            doc["gate"] = self.a.gate
        return doc


def parse_out(out):
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def parse_doc(p):
    doc = parse_out(p.stdout)
    if doc is None:
        return {"status": "fail", "error": "no result document (exit %d): %s" % (p.returncode, (p.stderr or p.stdout)[-800:]), "data": {}}
    doc.setdefault("data", {})
    return doc


def markdown(doc):
    lines = ["# knx-interop results", "", "Started %s, finished %s on %s/%s." % (doc["startedAt"], doc["finishedAt"], doc["host"]["platform"], doc["host"]["machine"]), "",
             "Summary: " + ", ".join("%s %d" % kv for kv in sorted(doc["summary"].items())), "", "## Implementations", "",
             "| Adapter | Implementation | Version | Roles |", "|---|---|---|---|"]
    for k, v in doc["implementations"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["implementation"], v["version"], ", ".join(v.get("roles") or [])))
    by = {}
    for r in doc["results"]:
        by.setdefault(r["suite"], []).append(r)
    for suite, rs in by.items():
        lines += ["", "## %s" % suite, "", "| Scenario | Client | Peer | Result | Detail |", "|---|---|---|---|---|"]
        for r in rs:
            detail = r.get("error") or r.get("detail") or (r.get("data") or {}).get("detail", "") or ""
            if r.get("observer"):
                detail = ("observer/responder %s. " % r["observer"]) + detail
            lines.append("| %s | %s | %s | %s | %s |" % (r["scenario"], r["client"], r["peer"], r["status"].upper(), detail.replace("|", "\\|").replace("\n", " ")[:300]))
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--registry", default=os.environ.get("REGISTRY", "ghcr.io/otfabric"))
    p.add_argument("--version", default=os.environ.get("VERSION", "dev"))
    p.add_argument("--servers", default=",".join(SERVERS))
    p.add_argument("--clients", default=",".join(CLIENTS))
    p.add_argument("--routers", default=",".join(ROUTERS))
    p.add_argument("--suites", default="tunnel,dpt,negative,routing,v2,secure,management")
    p.add_argument("--report", default="latest")
    p.add_argument("--gate", default="", help="fail only on failures involving this adapter (empty: any failure)")
    p.add_argument("--adapter", action="append", default=[], metavar="NAME=IMAGE",
                   help="an external adapter image (a system under test); it joins every role of its capabilities")
    a = p.parse_args()
    a.external = {}
    for spec in a.adapter:
        name, _, img = spec.partition("=")
        if not name or not img:
            p.error("--adapter %r: want NAME=IMAGE" % spec)
        a.external[name] = img
    a.servers = [s for s in a.servers.split(",") if s]
    a.clients = [s for s in a.clients.split(",") if s]
    a.routers = [s for s in a.routers.split(",") if s]
    a.suites = a.suites.split(",")
    m = Matrix(a)
    for name in a.external:
        roles = m.capabilities(name).get("roles", [])
        if "server" in roles and name not in a.servers:
            a.servers.insert(0, name)
        if "client" in roles:
            if name not in a.clients:
                a.clients.insert(0, name)
            if m.feature(name, "routing") and name not in a.routers:
                a.routers.insert(0, name)
    sh(["docker", "network", "create", "--driver", "bridge", m.net], check=True)
    try:
        for s in a.servers:
            m.capabilities(s)
        if {"tunnel", "dpt", "negative", "v2"} & set(a.suites):
            for s in a.servers:
                try:
                    m.tunnel_suite(s)
                except RuntimeError as e:
                    m.record("tunnel", "server start", "-", s, "fail", time.monotonic(), str(e))
        if "routing" in a.suites:
            m.routing_suite()
        if "secure" in a.suites:
            m.secure_suite()
        if "management" in a.suites:
            m.management_suite()
    finally:
        ids = sh(["docker", "ps", "-aq", "--filter", "network=" + m.net]).stdout.split()
        if ids:
            sh(["docker", "rm", "-f"] + ids)
        sh(["docker", "network", "rm", m.net])
    sys.exit(0 if m.report() else 1)


if __name__ == "__main__":
    main()
