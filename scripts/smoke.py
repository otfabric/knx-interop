#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Container-contract smoke test of one adapter image (scripts/smoke.sh).

    scripts/smoke.py <adapter> <image> <probe image>

Checks what needs no second stack: the capabilities document (contract 1.5,
with upstream.independentEngine), the KNX Secure test profile in an image
that declares a secure feature, a server that answers the probe's
DESCRIPTION_REQUEST on a private Docker network, a client operation that
cannot reach its target (one result document, fail, exit 1, or unsupported,
exit 3, when the adapter does not offer it) and a contract operation whose
feature the adapter declares false (unsupported, exit 3, never a fake
success). REPORT_DIR keeps the capabilities document.
"""

import json
import os
import subprocess
import sys
import time
import uuid

PROFILE = "/adapter/common/secure/profile.json"
# TEST-NET-1: nothing answers there.
UNREACHABLE = "192.0.2.1"
# Features that need the test profile.
SECURE = ("secure", "dataSecure", "secureUdp", "surrogate", "toolAccess")
# Client operations by the feature that declares them, in the order tried.
UNDECLARED = (("busmonitor", "busmonitor"), ("property", "property"), ("answer", "answer"),
              ("remoteProperty", "remote-property"), ("discover", "discover"))


def docker(*args, timeout=120):
    return subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)


def last_document(stdout):
    for line in reversed(stdout.strip().splitlines()):
        if line.strip().startswith("{"):
            return json.loads(line)
    raise ValueError("no JSON document on stdout")


class Smoke:
    def __init__(self, adapter, image, probe):
        self.adapter, self.image, self.probe = adapter, image, probe
        self.passed, self.failed = 0, 0
        self.network = "knxi-smoke-" + uuid.uuid4().hex[:8]

    def check(self, name, fn):
        try:
            reason = fn()
        except (subprocess.TimeoutExpired, OSError, ValueError, KeyError, TypeError) as e:
            reason = repr(e)
        if reason is None:
            self.passed += 1
            print("[smoke] ok   %s %s" % (self.adapter, name), flush=True)
        else:
            self.failed += 1
            print("[smoke] FAIL %s %s: %s" % (self.adapter, name, reason), flush=True)

    # -- checks ------------------------------------------------------
    def capabilities(self):
        p = docker("run", "--rm", self.image, "capabilities")
        if p.returncode != 0:
            return "exit %d: %s" % (p.returncode, p.stderr.strip()[-300:])
        doc = last_document(p.stdout)
        self.caps = doc
        if os.environ.get("REPORT_DIR"):
            os.makedirs(os.environ["REPORT_DIR"], exist_ok=True)
            with open(os.path.join(os.environ["REPORT_DIR"], "capabilities-%s.json" % self.adapter), "w") as f:
                json.dump(doc, f, indent=1, sort_keys=True)
                f.write("\n")
        problems = []
        if doc.get("schemaVersion") != "1.0":
            problems.append("schemaVersion %r" % doc.get("schemaVersion"))
        for key in ("implementation", "version"):
            if not isinstance(doc.get(key), str) or not doc[key]:
                problems.append("%s missing" % key)
        roles = doc.get("roles")
        if not isinstance(roles, list) or not roles or not set(roles) <= {"server", "client"}:
            problems.append("roles %r" % roles)
        if not isinstance(doc.get("features"), dict):
            problems.append("features is not an object")
        up = doc.get("upstream")
        if not isinstance(up, dict) or not isinstance(up.get("name"), str) or not isinstance(up.get("version"), str) \
                or not isinstance(up.get("independentEngine"), bool):
            problems.append("upstream {name, version, independentEngine} missing (contract 1.5): %r" % up)
        return "; ".join(problems) or None

    def profile(self):
        p = docker("run", "--rm", "--entrypoint", "cat", self.image, PROFILE)
        if p.returncode != 0:
            return "%s: %s" % (PROFILE, p.stderr.strip()[-200:])
        json.loads(p.stdout)
        return None

    def server(self):
        name = "knxi-smoke-srv-" + uuid.uuid4().hex[:6]
        p = docker("run", "-d", "--name", name, "--network", self.network, self.image, "server", "--name", "knx-interop")
        if p.returncode != 0:
            return "server did not start: " + p.stderr.strip()[-300:]
        try:
            ip = docker("inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name).stdout.strip()
            deadline = time.monotonic() + 90
            last = None
            while time.monotonic() < deadline:
                q = docker("run", "--rm", "--network", self.network, self.probe, "client", "describe", "--target", ip, "--timeout", "2")
                try:
                    last = last_document(q.stdout)
                except ValueError:
                    last = {"status": "no document", "error": q.stderr.strip()[-200:]}
                if last.get("status") == "pass":
                    return None
                time.sleep(1)
            logs = docker("logs", "--tail", "20", name)
            return "no DESCRIPTION_RESPONSE within 90 s (%s): %s" % (last, (logs.stdout + logs.stderr)[-500:])
        finally:
            docker("rm", "-f", name)

    def client(self, op, want, *extra):
        p = docker("run", "--rm", "--network", self.network, self.image, "client", op,
                   "--target", UNREACHABLE, "--timeout", "1", *extra, timeout=120)
        doc = last_document(p.stdout)
        exits = {"fail": 1, "unsupported": 3}
        if doc.get("status") not in want:
            return "status %r, want %s (%s)" % (doc.get("status"), " or ".join(want), doc.get("error"))
        if p.returncode != exits[doc["status"]]:
            return "status %s exits %d, want %d" % (doc["status"], p.returncode, exits[doc["status"]])
        if doc.get("op") != op or doc.get("schemaVersion") != "1.0":
            return "result document %r" % doc
        return None

    def run(self):
        self.check("capabilities", self.capabilities)
        caps = getattr(self, "caps", {})
        roles = caps.get("roles") or []
        features = caps.get("features") or {}
        server = features.get("server") or {}
        if any(features.get(f) for f in SECURE) or any(server.get(f) for f in SECURE + ("secureRouting",)):
            self.check("test profile", self.profile)
        docker("network", "create", "--driver", "bridge", self.network)
        try:
            if "server" in roles:
                self.check("server answers DESCRIPTION_REQUEST", self.server)
            if "client" in roles:
                want = ("fail",) if features.get("describe") else ("unsupported",)
                if self.adapter == "probe":
                    want = ("fail",)
                self.check("client describe, unreachable target", lambda: self.client("describe", want))
                undeclared = next((op for f, op in UNDECLARED if features.get(f) is False), None)
                if undeclared and self.adapter != "probe":
                    self.check("client %s, declared false" % undeclared,
                               lambda: self.client(undeclared, ("unsupported",), "--group", "1/0/1", "--dpt", "1.001", "--value", "1"))
        finally:
            docker("network", "rm", self.network)
        print("[smoke] %s: %d passed, %d failed" % (self.adapter, self.passed, self.failed), flush=True)
        return self.failed == 0 and self.passed > 0


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    return 0 if Smoke(*argv).run() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
