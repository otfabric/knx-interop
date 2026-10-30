#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare the upstream pin of one adapter with the latest upstream release.

    scripts/latest-upstream.py <adapter>

Prints key=value lines (the format of $GITHUB_OUTPUT):

    kind=library|image|package
    pin=<version the adapter pins>
    latest=<latest upstream release>
    update=yes|no
    source=<where the latest release was looked up>

The pins are read from the build inputs (Dockerfiles, requirements.txt,
package-lock.json): calimero-server and calimero-tools against the tags of
their official images on Docker Hub, knxd against the Debian suite of its
base image, xknx against PyPI, knxultimate against npm and goknx (knxctl)
against the Go module proxy. Snapshots and pre-releases are never "latest";
Calimero milestones (3.0-M1) are, as only they have images. probe is this
repository's own tool. Nothing is modified.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT = "knx-interop latest-upstream (https://github.com/otfabric/knx-interop)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": "application/json, */*"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


def read(path):
    return (ROOT / path).read_text()


def search(pattern, path):
    match = re.search(pattern, read(path), re.M)
    if not match:
        raise SystemExit(f"{path}: no pin matching {pattern}")
    return match.group(1)


def key(version):
    """Sort key of a stable release (v1.2.3, 1.2.3); None for anything else."""
    match = re.fullmatch(r"v?(\d+(?:\.\d+)*)", version)
    return tuple(int(part) for part in match.group(1).split(".")) if match else None


def milestone_key(version):
    """Sort key of a Calimero release (2.5-M1 < 2.5-rc2 < 2.5 < 3.0-M1); None
    for snapshots, architecture tags and latest."""
    match = re.fullmatch(r"(\d+(?:\.\d+)*)(?:-(M|rc)(\d+))?", version)
    if not match:
        return None
    stage = {"M": 1, "rc": 2, None: 3}[match.group(2)]
    return tuple(int(part) for part in match.group(1).split(".")) + ((stage, int(match.group(3) or 0)),)


def newest(versions, sort=key):
    stable = [v for v in versions if sort(v) is not None]
    if not stable:
        raise SystemExit("no release found upstream")
    return max(stable, key=sort)


def calimero(adapter, image):
    pin = search(rf"^FROM calimeroproject/{image}:([^@\s]+)@sha256:", f"adapters/{adapter}/Dockerfile")
    tags = json.loads(fetch(f"https://hub.docker.com/v2/repositories/calimeroproject/{image}/tags?page_size=100"))
    latest = newest([t["name"] for t in tags["results"]], milestone_key)
    return "image", pin, latest, f"Docker Hub calimeroproject/{image}"


def calimero_server():
    return calimero("calimero-server", "knxserver")


def calimero_tools():
    return calimero("calimero-tools", "knxtools")


def knxd():
    pin = search(r"^ARG KNXD_VERSION=(\S+)$", "adapters/knxd/Dockerfile")
    suite = search(r"^FROM \S*debian:([a-z]+)-slim@", "adapters/knxd/Dockerfile")
    versions = json.loads(fetch("https://sources.debian.org/api/src/knxd/"))["versions"]
    in_suite = [v["version"] for v in versions if suite in v["suites"]]
    if not in_suite:
        raise SystemExit(f"knxd is not in Debian {suite}")
    # One version per suite; Debian versions only move forward within it.
    latest = in_suite[0]
    return "package", pin, latest, f"Debian {suite}"


def xknx():
    pin = search(r"^xknx==(\S+)$", "adapters/xknx/requirements.txt")
    releases = json.loads(fetch("https://pypi.org/pypi/xknx/json"))["releases"]
    live = [v for v, files in releases.items() if files and not all(f.get("yanked") for f in files)]
    return "library", pin, newest(live), "PyPI"


def knxultimate():
    pin = json.loads(read("adapters/knxultimate/package-lock.json"))["packages"]["node_modules/knxultimate"]["version"]
    meta = json.loads(fetch("https://registry.npmjs.org/knxultimate"))
    live = [v for v, info in meta["versions"].items() if not info.get("deprecated")]
    return "library", pin, newest(live), "npm"


def goknx():
    pin = search(r"^ARG KNXCTL_VERSION=(\S+)$", "adapters/goknx/Dockerfile")
    versions = fetch("https://proxy.golang.org/github.com/otfabric/knxctl/@v/list").split()
    return "library", pin, newest(versions), "Go module proxy (knxctl)"


RESOLVERS = {
    "calimero-server": calimero_server,
    "calimero-tools": calimero_tools,
    "knxd": knxd,
    "xknx": xknx,
    "knxultimate": knxultimate,
    "goknx": goknx,
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in RESOLVERS:
        raise SystemExit(f"usage: latest-upstream.py {'|'.join(RESOLVERS)}")
    kind, pin, latest, source = RESOLVERS[sys.argv[1]]()
    print(f"kind={kind}")
    print(f"pin={pin}")
    print(f"latest={latest}")
    print(f"update={'yes' if latest != pin else 'no'}")
    print(f"source={source}")


if __name__ == "__main__":
    main()
