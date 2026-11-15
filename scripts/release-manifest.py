#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Writes manifest.json, the release asset that records what a release
published (.github/workflows/release.yml):

    scripts/release-manifest.py <vX.Y.Z> <commit> <digests file> <manifest.json>

The digests file holds one "<adapter> <sha256:...>" line per multi-arch image
the release created. Every image versions.yaml marks `published: true` needs
exactly one digest, and no other image may have one: otherwise nothing is
written and the exit status is 1. The upstream versions (and revisions, where
versions.yaml has them) of the published implementations come from
versions.yaml, which scripts/check-versions.py keeps equal to the build files.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = "ghcr.io/otfabric/knx-interop-"
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def read(path):
    with open(os.path.join(ROOT, path)) as f:
        return f.read()


def top(v, key):
    m = re.search(r'^%s: "([^"]+)"' % re.escape(key), v, re.M)
    if not m:
        raise SystemExit("versions.yaml has no %s" % key)
    return m.group(1)


def implementations(v):
    """{name: block} of the implementations section of versions.yaml."""
    section = re.search(r"^implementations:\n(.*?)(?=^\S|\Z)", v, re.M | re.S)
    return dict(re.findall(r"^  ([a-z0-9_-]+):\n((?:    .*\n)+)", section.group(1) if section else "", re.M))


def field(block, key):
    m = re.search(r'^    %s: "([^"]*)"' % re.escape(key), block, re.M)
    return m.group(1) if m else None


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    version, commit, digests_file, out = argv
    problems = []
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
        problems.append("%r is not vX.Y.Z" % version)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        problems.append("%r is not a commit" % commit)
    v = read("versions.yaml")
    if top(v, "interop_version") != version[1:]:
        problems.append("versions.yaml's interop_version is not %s" % version[1:])

    upstream, published = {}, []
    for name, block in implementations(v).items():
        if not re.search(r"^    published: true\b", block, re.M):
            continue
        pin = {"name": field(block, "upstream") or name, "version": field(block, "version") or ""}
        if field(block, "revision"):
            pin["revision"] = field(block, "revision")
        upstream[name] = pin
        if os.path.isfile(os.path.join(ROOT, "adapters", name, "Dockerfile")):
            published.append(name)
    if not published:
        problems.append("versions.yaml marks no image published: true")

    digests = {}
    try:
        with open(digests_file) as f:
            lines = f.read().splitlines()
    except OSError as e:
        lines = []
        problems.append("%s: %s" % (digests_file, e.strerror))
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2 or not DIGEST.fullmatch(parts[1]):
            problems.append("%s:%d: not \"<adapter> sha256:<64 hex>\": %r" % (digests_file, n, line.strip()))
        elif parts[0] in digests:
            problems.append("%s: two digests for %s" % (digests_file, parts[0]))
        else:
            digests[parts[0]] = parts[1]
    for name in published:
        if name not in digests:
            problems.append("no digest for %s, which versions.yaml publishes" % name)
    for name in sorted(set(digests) - set(published)):
        problems.append("a digest for %s, which versions.yaml does not publish" % name)

    if problems:
        for p in problems:
            print("release-manifest: %s" % p, file=sys.stderr)
        return 1
    manifest = {
        "repository": "github.com/otfabric/knx-interop",
        "version": version,
        "commit": commit,
        "contract": top(v, "contract_version"),
        "platforms": ["linux/amd64", "linux/arm64"],
        "upstream": upstream,
        "images": {name: "%s%s@%s" % (REGISTRY, name, digests[name]) for name in published},
    }
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
