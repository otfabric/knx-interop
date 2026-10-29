#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run the knx-interop scenarios between every pair of adapters on an
isolated Docker bridge network, and write reports/<name>.json and .md.

Every scenario runs real implementations in containers; nothing is
simulated. A result is pass, fail, unsupported (an adapter or stack does not
offer the operation) or not-tested (a prerequisite failed).

Usage: run-matrix.py [--registry R] [--version V] [--servers a,b] [--clients a,b]
                     [--suites tunnel,dpt,negative,routing] [--report NAME]
"""

import argparse
import datetime
import fnmatch
import json
import os
import subprocess
import sys
import threading
import time
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVERS = ["goknx", "knxd", "calimero-server"]
CLIENTS = ["goknx", "xknx", "knxultimate", "calimero-tools", "knxd"]
ROUTERS = ["goknx", "xknx", "knxultimate", "calimero-tools", "knxd"]
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
            c, p, sc, reason = line.rstrip("\n").split("\t", 3)
            known.append((c, p, sc, reason))
    return known


class Matrix:
    def __init__(self, a):
        self.a = a
        self.known = load_known()
        self.net = "knxi-" + uuid.uuid4().hex[:8]
        self.results = []
        self.caps = {}
        self.started = datetime.datetime.now(datetime.timezone.utc)

    def image(self, adapter):
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

    def start_server(self, adapter, routing=False):
        name = "knxi-srv-%s-%s" % (adapter, uuid.uuid4().hex[:6])
        args = ["docker", "run", "-d", "--name", name, "--network", self.net, self.image(adapter), "server", "--name", SERVER_NAME]
        if routing:
            args.append("--routing")
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
        if status == "fail":
            for kc, kp, ks, reason in self.known:
                if fnmatch.fnmatch(client, kc) and fnmatch.fnmatch(peer, kp) and fnmatch.fnmatch(scenario, ks):
                    status, error = "known-difference", "%s (observed: %s)" % (reason, error)
                    break
        r = {"suite": suite, "scenario": scenario, "client": client, "peer": peer, "status": status,
             "durationMs": int((time.monotonic() - start) * 1000)}
        for adapter, key in ((client, "clientVersion"), (peer, "peerVersion")):
            if adapter in self.caps:
                r[key] = self.caps[adapter].get("version")
        if observer:
            r["observer"] = observer
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
        return "goknx" if client != "goknx" else "xknx"

    def responder_for(self, client):
        return "xknx" if client != "xknx" else "goknx"

    def tunnel_suite(self, server):
        name, ip = self.start_server(server)
        try:
            for c in self.a.clients:
                self.capabilities(c)
                if "tunnel" in self.a.suites:
                    self.discover(c, server, ip)
                    self.describe(c, server, ip)
                    self.connect(c, server, ip)
                    self.write(c, server, ip)
                    self.read(c, server, ip)
                if "dpt" in self.a.suites:
                    self.dpt(c, server, ip)
            if "negative" in self.a.suites:
                self.negative(server, ip)
        finally:
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

    def write(self, c, server, ip, vector=None, scenario="group write (DPT 1.001)", suite="tunnel"):
        v = vector or {"dpt": "1.001", "group": "1/0/1", "value": "on", "data": "01"}
        t = time.monotonic()
        o = self.observer_for(c)
        h = self.background(o, "monitor", ["--target", ip, "--count", "1", "--timeout", "15"])
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record(suite, scenario, c, server, "not-tested", t, "observer %s could not listen: %s" % (o, res.get("error")), observer=o)
        r = self.client(c, "write", ["--target", ip, "--group", v["group"], "--dpt", v["dpt"], "--value", v["value"], "--data", v["data"]])
        obs = self.collect(h)
        if r["status"] != "pass":
            return self.record(suite, scenario, c, server, r["status"], t, r.get("error"), observer=o)
        seen = [x for x in obs.get("data", {}).get("telegrams", []) if x.get("group") == v["group"] and x.get("service") == "write"]
        if not seen:
            return self.record(suite, scenario, c, server, "fail", t, "observer %s saw no write to %s: %s" % (o, v["group"], obs.get("error") or obs.get("data")), observer=o)
        ok = seen[0].get("data", "").upper() == v["data"]
        self.record(suite, scenario, c, server, "pass" if ok else "fail", t,
                    None if ok else "observer %s saw %s, expected %s" % (o, seen[0].get("data"), v["data"]), {"seen": seen[0]}, observer=o)

    def read(self, c, server, ip):
        t = time.monotonic()
        scenario = "group read/response (DPT 9.001)"
        resp = self.responder_for(c)
        h = self.background(resp, "answer", ["--target", ip, "--group", "1/0/2", "--dpt", "9.001", "--value", "21.5", "--data", "0C33", "--count", "1", "--timeout", "20"])
        if not h["ready"]:
            res = self.collect(h, 30)
            return self.record("tunnel", scenario, c, server, "not-tested", t, "responder %s: %s" % (resp, res.get("error")), observer=resp)
        r = self.client(c, "read", ["--target", ip, "--group", "1/0/2", "--dpt", "9.001", "--timeout", "8"])
        sh(["docker", "rm", "-f", h["name"]])
        h["proc"].wait(10)
        if r["status"] != "pass":
            return self.record("tunnel", scenario, c, server, r["status"], t, r.get("error"), observer=resp)
        d = r["data"]
        ok = d.get("data", "").upper() == "0C33" or str(d.get("value")).startswith("21.5")
        self.record("tunnel", scenario, c, server, "pass" if ok else "fail", t, None if ok else "response %r" % d, d, observer=resp)

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
        return summary.get("fail", 0) == 0


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
    p.add_argument("--suites", default="tunnel,dpt,negative,routing")
    p.add_argument("--report", default="latest")
    a = p.parse_args()
    a.servers = [s for s in a.servers.split(",") if s]
    a.clients = [s for s in a.clients.split(",") if s]
    a.routers = [s for s in a.routers.split(",") if s]
    a.suites = a.suites.split(",")
    m = Matrix(a)
    sh(["docker", "network", "create", "--driver", "bridge", m.net], check=True)
    try:
        for s in a.servers:
            m.capabilities(s)
        if {"tunnel", "dpt", "negative"} & set(a.suites):
            for s in a.servers:
                try:
                    m.tunnel_suite(s)
                except RuntimeError as e:
                    m.record("tunnel", "server start", "-", s, "fail", time.monotonic(), str(e))
        if "routing" in a.suites:
            m.routing_suite()
    finally:
        ids = sh(["docker", "ps", "-aq", "--filter", "network=" + m.net]).stdout.split()
        if ids:
            sh(["docker", "rm", "-f"] + ids)
        sh(["docker", "network", "rm", m.net])
    sys.exit(0 if m.report() else 1)


if __name__ == "__main__":
    main()
