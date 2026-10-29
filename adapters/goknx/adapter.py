#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""knx-interop adapter for go-knx, through knxctl (the system under test)."""

import json
import os
import subprocess
import sys

sys.path.insert(0, "/adapter/common")
import contract  # noqa: E402

IMPL = "go-knx"
KNXCTL = os.environ.get("KNXCTL", "/usr/local/bin/knxctl")


def version():
    try:
        out = subprocess.run([KNXCTL, "version", "--format", "json"], capture_output=True, text=True, timeout=10).stdout
        r = json.loads(out)["result"]
        return r.get("goKnx", "unknown") + " (knxctl " + r.get("version", "?") + ")"
    except Exception:  # noqa: BLE001
        return "unknown"


def link(a):
    if a.routing:
        return ["--routing"]
    args = ["--gateway", "%s:%d" % (a.target, a.port)]
    if a.nat:
        args.append("--nat")
    return args


def knxctl(args, timeout):
    p = subprocess.run([KNXCTL, "--format", "json", "--timeout", "%gs" % timeout] + args,
                       capture_output=True, text=True, timeout=timeout + 30)
    return p


def last_doc(stdout):
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                pass
    try:
        return json.loads(stdout)
    except ValueError:
        return None


def main():
    a = contract.parser().parse_args()
    if a.role == "capabilities":
        contract.capabilities(IMPL, version(), ["server", "client"],
                              {"discover": True, "describe": True, "tunnel": True, "routing": True, "nat": True,
                               "answer": True, "secure": False})
        return
    if a.role == "server":
        args = [KNXCTL, "serve", "--name", a.name[:30], "--tunnels", ",".join("1.1.%d" % i for i in range(10, 18)),
                "--address", "1.1.0", "--device-address", "1.1.1",
                "--object", "1/0/1:1.001:CRWU=off", "--object", "1/0/2:9.001:CRWU=21.5", "--object", "1/0/3:5.001:CRWU=50",
                "--object", "1/0/4:14.056:CRWU=1234.5", "--object", "1/0/5:16.000:CRWU=interop"]
        if a.routing:
            args += ["--routing", "--interface", "eth0"]
        contract.ready()
        os.execv(KNXCTL, args)
    r = contract.Result(IMPL, version(), a.op)
    try:
        if a.op == "discover":
            p = knxctl(["discover", "--interface", "eth0"], a.timeout)
            doc = last_doc(p.stdout)
            if p.returncode != 0 or not doc:
                r.finish("fail", error=p.stderr or p.stdout)
            devs = [{"endpoint": d["endpoint"], "name": d["name"], "address": d["individualAddress"]} for d in doc["result"]["devices"]]
            r.finish("pass", {"devices": devs})
        if a.op == "describe":
            args = ["describe", "%s:%d" % (a.target, a.port)] + (["--nat"] if a.nat else [])
            p = knxctl(args, a.timeout)
            doc = last_doc(p.stdout)
            if p.returncode != 0 or not doc or "result" not in doc:
                r.finish("fail", error=p.stderr or p.stdout)
            d = doc["result"]["device"]
            r.finish("pass", {"name": d["name"], "address": d["individualAddress"], "services": d["services"]})
        if a.op == "connect":
            args = ["tunnel", "connect", "%s:%d" % (a.target, a.port)] + (["--nat"] if a.nat else [])
            p = knxctl(args, a.timeout)
            doc = last_doc(p.stdout)
            if p.returncode != 0 or not doc or "result" not in doc:
                r.finish("fail", error=p.stderr or p.stdout)
            d = doc["result"]
            r.finish("pass", {"channel": d["channel"], "address": d["individualAddress"]})
        if a.op == "write":
            p = knxctl(["group", "write", "--dpt", a.dpt] + link(a) + ["--", a.group, a.value], a.timeout)
            doc = last_doc(p.stdout)
            if p.returncode != 0:
                r.finish("fail", error=p.stderr or p.stdout)
            r.finish("pass", {"data": doc["result"]["data"]})
        if a.op == "read":
            p = knxctl(["group", "read", a.group, "--dpt", a.dpt] + link(a), a.timeout)
            doc = last_doc(p.stdout)
            if p.returncode != 0 or not doc or "result" not in doc:
                r.finish("fail", error=p.stderr or p.stdout)
            t = doc["result"]["responses"][0]
            r.finish("pass", {"source": t["source"], "data": t.get("data", ""), "value": t.get("value")})
        if a.op in ("monitor", "answer"):
            if a.op == "monitor":
                args = ["monitor", "--count", str(a.count), "--duration", "%gs" % a.timeout] + link(a)
            else:
                args = ["group", "answer", "--dpt", a.dpt, "--count", str(a.count), "--duration", "%gs" % a.timeout] + link(a) + ["--", a.group, a.value]
            p = subprocess.Popen([KNXCTL, "--format", "json", "--timeout", "5s"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # knxctl prints "listening"/"answering" on stderr once connected.
            for line in p.stderr:
                if "listening" in line or "answering" in line:
                    contract.ready()
                    break
                sys.stderr.write(line)
            out, err = p.communicate(timeout=a.timeout + 30)
            if p.returncode != 0:
                r.finish("fail", error=err or out)
            if a.op == "answer":
                doc = last_doc(out)
                r.finish("pass", {"answered": doc["result"]["answered"]})
            tel = []
            for line in out.splitlines():
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "telegram":
                    tel.append({"source": d["source"], "group": d["group"], "service": d["service"], "data": d.get("data", "")})
            r.finish("pass" if len(tel) >= a.count else "fail", {"telegrams": tel},
                     None if len(tel) >= a.count else "received %d of %d telegrams" % (len(tel), a.count))
    except subprocess.TimeoutExpired as e:
        r.finish("fail", error="timeout: %s" % e)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        r.finish("fail", error=repr(e))


if __name__ == "__main__":
    main()
