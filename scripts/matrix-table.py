#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Print the feature × implementation matrix of a report (Markdown), as in
docs/INTEROPERABILITY.md."""

import json
import sys

COLS = [("calimero", ["calimero-tools", "calimero-server"]), ("knxd", ["knxd"]), ("xknx", ["xknx"]),
        ("KNXUltimate", ["knxultimate"]), ("go-knx", ["goknx"])]
MARK = {"pass": "PASS", "fail": "FAIL", "unsupported": "UNSUPPORTED", "not-tested": "NOT TESTED", "known-difference": "KNOWN DIFFERENCE"}


def cell(results, adapters, pred):
    rs = [r for r in results if pred(r, adapters)]
    if not rs:
        return "NOT TESTED"
    c = {}
    for r in rs:
        c[r["status"]] = c.get(r["status"], 0) + 1
    if set(c) == {"pass"}:
        return "PASS (%d)" % c["pass"]
    return ", ".join("%s %d" % (MARK[k], v) for k, v in sorted(c.items()))


def main():
    d = json.load(open(sys.argv[1]))
    res = [r for r in d["results"] if "goknx" in (r["client"], r["peer"]) or r["suite"] == "negative"] if "--goknx" in sys.argv else d["results"]
    rows = [
        ("Discovery (as client)", lambda r, a: r["scenario"].startswith("discover") and r["client"] in a),
        ("Description (as client)", lambda r, a: r["scenario"] == "describe" and r["client"] in a),
        ("Tunnelling client", lambda r, a: r["scenario"] == "connect and disconnect" and r["client"] in a),
        ("Tunnelling server", lambda r, a: r["suite"] == "tunnel" and r["scenario"] in ("connect and disconnect", "group write (DPT 1.001)") and r["peer"] in a),
        ("Group write", lambda r, a: r["scenario"].startswith("group write") and r["client"] in a),
        ("Group read (client)", lambda r, a: r["scenario"].startswith("group read") and r["client"] in a),
        ("Group response (responder/observer)", lambda r, a: r["scenario"].startswith("group read") and r.get("observer") in a),
        ("Routing (sender)", lambda r, a: r["suite"] == "routing" and r["client"] in a),
        ("Routing (receiver)", lambda r, a: r["suite"] == "routing" and r["peer"] in a),
        ("DPT encoding (sender)", lambda r, a: r["suite"] == "dpt" and r["client"] in a),
        ("DPT decoding (observer)", lambda r, a: r["suite"] == "dpt" and r.get("observer") in a),
        ("Negative tests (server)", lambda r, a: r["suite"] == "negative" and r["peer"] in a),
        ("Tunnelling over TCP (client)", lambda r, a: r["suite"] == "v2" and "TCP" in r["scenario"] and r["client"] in a),
        ("Tunnelling over TCP (server)", lambda r, a: r["suite"] == "v2" and "TCP" in r["scenario"] and r["peer"] in a),
        ("Device management (client)", lambda r, a: r["suite"] == "v2" and r["scenario"].startswith("device management") and r["client"] in a),
        ("Device management (server)", lambda r, a: r["suite"] == "v2" and r["scenario"].startswith("device management") and r["peer"] in a),
        ("Busmonitor (client)", lambda r, a: r["suite"] == "v2" and r["scenario"].startswith("busmonitor") and r["client"] in a),
        ("Busmonitor (server)", lambda r, a: r["suite"] == "v2" and r["scenario"].startswith("busmonitor") and r["peer"] in a),
        ("IP Secure tunnelling (client)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith(("secure session", "secure tunnel", "secure group")) and "UDP" not in r["scenario"] and r["client"] in a),
        ("IP Secure tunnelling (server)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith(("secure session", "secure tunnel", "secure group", "plain connection", "secure tunnelling server")) and "UDP" not in r["scenario"] and r["peer"] in a),
        ("IP Secure sessions over UDP (client)", lambda r, a: r["suite"] == "secure" and "UDP" in r["scenario"] and r["client"] in a),
        ("IP Secure sessions over UDP (server)", lambda r, a: r["suite"] == "secure" and "UDP" in r["scenario"] and r["peer"] in a),
        ("IP Secure device management (client)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("secure device management") and r["client"] in a),
        ("IP Secure device management (server)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("secure device management") and r["peer"] in a),
        ("IP Secure routing (sender)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("secure routing") and "server" not in r["scenario"] and r["client"] in a),
        ("IP Secure routing (receiver)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("secure routing") and "server" not in r["scenario"] and r["peer"] in a),
        ("IP Secure routing (server)", lambda r, a: r["suite"] == "secure" and "the server" in r["scenario"] and r["peer"] in a),
        ("Data Secure (sender)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("Data Secure") and r["client"] in a),
        ("Data Secure (receiver)", lambda r, a: r["suite"] == "secure" and r["scenario"].startswith("Data Secure") and (r.get("observer") or r["peer"]) in a),
    ]
    print("| Feature | " + " | ".join(c for c, _ in COLS) + " |")
    print("|---|" + "---|" * len(COLS))
    for name, pred in rows:
        print("| %s | %s |" % (name, " | ".join(cell(res, a, pred) for _, a in COLS)))


if __name__ == "__main__":
    main()
