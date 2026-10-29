#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the fixtures: every DPT vector has the fields the runner needs,
and its data is the encoding the standard's format rules give (recomputed
here from first principles, independently of every implementation)."""

import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def f16(x):
    for e in range(16):
        m = x * 100 / 2 ** e
        if -2048 <= round(m) <= 2047:
            if abs(m - round(m)) == 0.5:
                raise ValueError("%s is a rounding tie: implementations may differ" % x)
            m = round(m)
            return "%04X" % ((e << 11) | (m & 0x7FF) | (0x8000 if m < 0 else 0))


def expected(d, val):
    if d.startswith("9."):
        return f16(float(val))
    if d.startswith("14."):
        return struct.pack(">f", float(val)).hex().upper()
    if d.startswith("12."):
        return "%08X" % int(val)
    if d.startswith("13."):
        return struct.pack(">i", int(val)).hex().upper()
    if d.startswith("7."):
        return "%04X" % int(val)
    if d == "5.010":
        return "%02X" % int(val)
    if d == "5.001":
        return "%02X" % round(float(val) * 255 / 100)
    if d.startswith("16."):
        return val.encode("latin-1").ljust(14, b"\0").hex().upper()
    if d.startswith("1."):
        return {"on": "01", "off": "00"}[val]
    raise ValueError("no rule for %s" % d)


def main():
    doc = json.load(open(os.path.join(ROOT, "fixtures", "dpt-vectors.json")))
    bad = 0
    for v in doc["vectors"]:
        for k in ("dpt", "group", "value", "data", "small"):
            if k not in v:
                print("vector %r lacks %s" % (v, k))
                bad += 1
        try:
            e = expected(v["dpt"], v["value"])
        except ValueError as err:
            print("vector %r: %s" % (v, err))
            bad += 1
            continue
        if e != v["data"]:
            print("vector %s %s: data %s, rules give %s" % (v["dpt"], v["value"], v["data"], e))
            bad += 1
    if bad:
        sys.exit(1)
    print("%d DPT vectors valid" % len(doc["vectors"]))


if __name__ == "__main__":
    main()
