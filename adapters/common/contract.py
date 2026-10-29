# SPDX-License-Identifier: MIT
"""The knx-interop container contract (docs/CONTAINER_CONTRACT.md) for
Python adapters: argument parsing and the result document."""

import argparse
import json
import sys
import time

SCHEMA_VERSION = "1.0"

OPS = ["discover", "describe", "connect", "write", "read", "monitor", "answer", "property", "busmonitor"]


def parser():
    p = argparse.ArgumentParser(prog="run")
    sub = p.add_subparsers(dest="role", required=True)
    sub.add_parser("capabilities")
    s = sub.add_parser("server")
    s.add_argument("--routing", action="store_true")
    s.add_argument("--name", default="knx-interop")
    s.add_argument("--secure", action="store_true", help="KNX IP Secure with the test profile (common/secure)")
    c = sub.add_parser("client")
    c.add_argument("op", choices=OPS)
    c.add_argument("--target", default="")
    c.add_argument("--port", type=int, default=3671)
    c.add_argument("--nat", action="store_true")
    c.add_argument("--routing", action="store_true")
    c.add_argument("--tcp", action="store_true", help="tunnel over TCP (KNXnet/IP core v2)")
    c.add_argument("--secure", action="store_true",
                   help="KNX IP Secure (secure session or secure routing) and KNX Data Secure with the test profile (common/secure)")
    c.add_argument("--user", type=int, default=2, help="secure tunnelling user of the test profile (1 management, 2, 3)")
    c.add_argument("--object", type=int, default=0, help="property: interface object type (0 device)")
    c.add_argument("--pid", type=int, default=11, help="property: property identifier (11 serial number)")
    c.add_argument("--group", default="")
    c.add_argument("--dpt", default="")
    c.add_argument("--value", default="")
    c.add_argument("--data", default="", help="the expected encoding of --value, hexadecimal (for adapters without a DPT codec)")
    c.add_argument("--count", type=int, default=1)
    c.add_argument("--timeout", type=float, default=5.0)
    return p


class Result:
    """Collects the result of one operation and prints it as the last line
    of stdout."""

    def __init__(self, implementation, version, op):
        self.doc = {
            "schemaVersion": SCHEMA_VERSION,
            "implementation": implementation,
            "version": version,
            "op": op,
            "status": "fail",
            "durationMs": 0,
            "data": {},
        }
        self.start = time.monotonic()

    def finish(self, status, data=None, error=None):
        self.doc["status"] = status
        self.doc["durationMs"] = int((time.monotonic() - self.start) * 1000)
        if data is not None:
            self.doc["data"] = data
        if error:
            self.doc["error"] = str(error)[:2000]
        sys.stdout.write(json.dumps(self.doc, sort_keys=True) + "\n")
        sys.stdout.flush()
        sys.exit({"pass": 0, "fail": 1, "unsupported": 3}[status])


# The KNX Secure test profile (contract 1.2): public test values only.
SECURE_DIR = "/adapter/common/secure"


def secure_profile():
    with open(SECURE_DIR + "/profile.json") as f:
        p = json.load(f)
    p["keyringPath"] = SECURE_DIR + "/" + p["keyring"]
    return p


def ready():
    """Signal that a long-running operation (server, monitor, answer) is
    listening."""
    sys.stderr.write("READY\n")
    sys.stderr.flush()


def capabilities(implementation, version, roles, features, notes=""):
    doc = {
        "schemaVersion": SCHEMA_VERSION,
        "implementation": implementation,
        "version": version,
        "roles": roles,
        "features": features,
    }
    if notes:
        doc["notes"] = notes
    sys.stdout.write(json.dumps(doc, sort_keys=True) + "\n")
