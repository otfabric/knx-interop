#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail when versions.yaml disagrees with the build inputs (Dockerfiles,
requirements, package lock, go.mod): every pin is read from versions.yaml and
compared with the file the build takes it from. Also checks that
adapters/xknx/requirements.txt pins every distribution with its hashes, that
`published` matches the release's PUBLISHED, and that adapters/LICENSE (the
copy the images take, inside their build context) is the repository's
LICENSE. Reads the YAML subset this repository uses without third-party
modules."""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(p):
    with open(os.path.join(ROOT, p)) as f:
        return f.read()


def implementations(v):
    """{name: block} of the implementations section of versions.yaml."""
    section = re.search(r"^implementations:\n(.*?)(?=^\S|\Z)", v, re.M | re.S)
    return dict(re.findall(r"^  ([a-z0-9_-]+):\n((?:    .*\n)+)", section.group(1) if section else "", re.M))


def field(block, key):
    m = re.search(r'^    %s: "([^"]*)"' % re.escape(key), block, re.M)
    return m.group(1) if m else None


def requirements(text):
    """The requirements of a pip requirements file, continuation lines joined,
    comments dropped."""
    joined = re.sub(r"\\\n", " ", text)
    return [line.strip() for line in (l.split(" #")[0] for l in joined.splitlines())
            if line.strip() and not line.strip().startswith("#")]


def main():
    v = read("versions.yaml")
    impl = implementations(v)
    errors = []

    def want(cond, msg):
        if not cond:
            errors.append(msg)

    for name, digest in re.findall(r'^\s+(python|node|debian|golang): "[^"@]+@(sha256:[0-9a-f]{64})"', v, re.M):
        # The adapters, and the images of OT Fabric's own stacks (own/).
        dirs = [os.path.join(top, f) for top in ("adapters", "own") if os.path.isdir(os.path.join(ROOT, top))
                for f in os.listdir(os.path.join(ROOT, top)) if os.path.isdir(os.path.join(ROOT, top, f))]
        used = any(digest in read(os.path.join(f, d)) for f in dirs
                   for d in os.listdir(os.path.join(ROOT, f)) if d.startswith("Dockerfile"))
        want(used, "base image %s %s is used by no Dockerfile" % (name, digest))
    def pin(name, key):
        value = field(impl.get(name, ""), key)
        want(value, "versions.yaml: %s has no %s" % (name, key))
        return value or "\0"

    # Calimero: the official images, by tag and digest.
    for name in ("calimero-server", "calimero-tools"):
        image, version = pin(name, "image"), pin(name, "version")
        dockerfile = read("adapters/%s/Dockerfile" % name)
        want(re.search(r"^FROM %s$" % re.escape(image), dockerfile, re.M),
             "%s: the Dockerfile's FROM is not versions.yaml's image %s" % (name, image))
        want(re.search(r"^[^:@]+:%s@sha256:[0-9a-f]{64}$" % re.escape(version), image),
             "%s: versions.yaml's image %s is not version %s by digest" % (name, image, version))
        want('RUN echo "%s" > /adapter/VERSION' % version in dockerfile,
             "%s: the Dockerfile's /adapter/VERSION is not %s" % (name, version))
    # knxd: the Debian package.
    knxd = pin("knxd", "version")
    want("ARG KNXD_VERSION=%s\n" % knxd in read("adapters/knxd/Dockerfile"),
         "knxd: the Dockerfile's KNXD_VERSION is not versions.yaml's %s" % knxd)
    # xknx: requirements.in names it, requirements.txt locks it and every
    # dependency with hashes.
    xknx = pin("xknx", "version")
    want(re.search(r"^xknx==%s$" % re.escape(xknx), read("adapters/xknx/requirements.in"), re.M),
         "xknx: adapters/xknx/requirements.in does not pin versions.yaml's %s" % xknx)
    locked = requirements(read("adapters/xknx/requirements.txt"))
    want(locked, "xknx: adapters/xknx/requirements.txt has no requirement")
    for line in locked:
        m = re.match(r"([A-Za-z0-9._-]+)==([^\s;]+)(?:\s*;.*?)?((?:\s+--hash=sha256:[0-9a-f]{64})+)$", line)
        want(m, "xknx: requirements.txt: not pinned with == and --hash=sha256: %s" % line[:80])
        if m and m.group(1) == "xknx":
            want(m.group(2) == xknx, "xknx: requirements.txt locks xknx %s, versions.yaml says %s" % (m.group(2), xknx))
    for line in requirements(read("adapters/xknx/requirements.in")):
        name, _, version = line.partition("==")
        want(any(re.match(r"%s==%s\b" % (re.escape(name), re.escape(version)), l, re.I) for l in locked),
             "xknx: requirements.txt does not lock %s (make lock-xknx)" % line)
    # knxultimate: package.json and the lock.
    knxu = pin("knxultimate", "version")
    lock = json.loads(read("adapters/knxultimate/package-lock.json"))
    want(lock["packages"].get("node_modules/knxultimate", {}).get("version") == knxu,
         "knxultimate: package-lock.json does not install versions.yaml's %s" % knxu)
    want(json.loads(read("adapters/knxultimate/package.json")).get("dependencies", {}).get("knxultimate") == knxu,
         "knxultimate: package.json does not pin versions.yaml's %s" % knxu)
    # published: what the release publishes (release.yml PUBLISHED, the
    # Makefile's PUBLISHED_ADAPTERS), for the implementations with an adapter.
    published = set()
    for name, block in impl.items():
        if not re.search(r"^    status: implemented\b", block, re.M):
            continue
        flag = re.search(r"^    published: (true|false)\b", block, re.M)
        want(flag, "versions.yaml: %s has no published: true or false" % name)
        if flag and flag.group(1) == "true" and os.path.isfile(os.path.join(ROOT, "adapters", name, "Dockerfile")):
            published.add(name)
    release = re.search(r'^  PUBLISHED: "([^"]*)"$', read(".github/workflows/release.yml"), re.M)
    makefile = re.search(r"^PUBLISHED_ADAPTERS \?= (.*)$", read("Makefile"), re.M)
    for where, m in (("release.yml PUBLISHED", release), ("the Makefile's PUBLISHED_ADAPTERS", makefile)):
        names = set(m.group(1).split()) if m else None
        want(names == published, "published: versions.yaml says %s, %s %s" % (
            " ".join(sorted(published)), where, " ".join(sorted(names)) if names is not None else "is missing"))
    want(read("adapters/LICENSE") == read("LICENSE"), "adapters/LICENSE is not a copy of LICENSE")
    # cbsigma: go.mod is the pin; versions.yaml and the Dockerfile's commits mirror it.
    gomod, cbdock, gosum = read("adapters/cbsigma/go.mod"), read("adapters/cbsigma/Dockerfile"), read("adapters/cbsigma/go.sum")
    for module, key, arg in (("github.com/cB-Sigma/knx", "cbsigma", "UPSTREAM_SHA"), ("github.com/cB-Sigma/knx-sim", "cbsigma_sim", "SIM_SHA")):
        pin = re.search(r"^\s*%s (v\S+)$" % re.escape(module), gomod, re.M)
        block = re.search(r"^  %s:\n((?:    .*\n)+)" % key, v, re.M)
        want(pin is not None and block is not None, "%s in adapters/cbsigma/go.mod and versions.yaml" % module)
        if pin and block:
            want('version: "%s"' % pin.group(1) in block.group(1), "%s %s: versions.yaml %s" % (module, pin.group(1), key))
            sha = re.search(r'revision: "([0-9a-f]{40})"', block.group(1))
            want(sha is not None and ("ARG %s=%s" % (arg, sha.group(1))) in cbdock, "%s commit in versions.yaml and the Dockerfile" % module)
            want(("%s %s h1:" % (module, pin.group(1))) in gosum, "%s %s in go.sum" % (module, pin.group(1)))
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
