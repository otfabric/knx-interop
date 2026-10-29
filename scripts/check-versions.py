#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail when versions.yaml disagrees with the build inputs (Dockerfiles,
requirements, package lock). Reads the YAML subset this repository uses
without third-party modules."""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(p):
    with open(os.path.join(ROOT, p)) as f:
        return f.read()


def main():
    v = read("versions.yaml")
    errors = []

    def want(cond, msg):
        if not cond:
            errors.append(msg)

    for name, digest in re.findall(r'^\s+(python|node|debian|golang): "[^"@]+@(sha256:[0-9a-f]{64})"', v, re.M):
        files = [f for f in os.listdir(os.path.join(ROOT, "adapters")) if os.path.isdir(os.path.join(ROOT, "adapters", f))]
        used = any(digest in read("adapters/%s/%s" % (f, d)) for f in files
                   for d in os.listdir(os.path.join(ROOT, "adapters", f)) if d.startswith("Dockerfile"))
        want(used, "base image %s %s is used by no Dockerfile" % (name, digest))
    for d in ("70463ad74c4c976cbc8c062fc219b19059f417562051670deeaa65c5e13f7f9c",):
        want(d in read("adapters/calimero-server/Dockerfile") and d in v, "calimero-server digest")
    want("c83aa43c4a61f237104f08952d205cacab17d574040b46d5861b05cba4119966" in read("adapters/calimero-tools/Dockerfile"), "calimero-tools digest")
    want(re.search(r"^xknx==4\.0\.0$", read("adapters/xknx/requirements.txt"), re.M) is not None, "xknx pin in requirements.txt")
    lock = json.loads(read("adapters/knxultimate/package-lock.json"))
    want(lock["packages"]["node_modules/knxultimate"]["version"] == "6.3.1", "knxultimate version in package-lock.json")
    want("ARG KNXD_VERSION=0.14.73-1" in read("adapters/knxd/Dockerfile"), "knxd package version")
    iv = re.search(r'^interop_version: "([^"]+)"', v, re.M).group(1)
    rel = read("RELEASE.md") if os.path.exists(os.path.join(ROOT, "RELEASE.md")) else ""
    want("## v" + iv in rel, "RELEASE.md has no section ## v%s" % iv)
    for e in errors:
        print("versions:", e)
    if errors:
        sys.exit(1)
    print("versions.yaml agrees with the build inputs")


if __name__ == "__main__":
    main()
