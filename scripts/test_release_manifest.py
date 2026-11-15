#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests of scripts/release-manifest.py, which writes the release's
manifest.json and refuses a release without the digest of every published
image."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(HERE, "release-manifest.py")
COMMIT = "0123456789abcdef0123456789abcdef01234567"

with open(os.path.join(ROOT, "versions.yaml")) as f:
    VERSIONS = f.read()
VERSION = "v" + re.search(r'^interop_version: "([^"]+)"', VERSIONS, re.M).group(1)
with open(os.path.join(ROOT, ".github", "workflows", "release.yml")) as f:
    PUBLISHED = re.search(r'^  PUBLISHED: "([^"]*)"$', f.read(), re.M).group(1).split()


def digest(n):
    return "sha256:%064x" % n


class ReleaseManifest(unittest.TestCase):
    def run_with(self, lines, version=VERSION, commit=COMMIT):
        with tempfile.TemporaryDirectory() as tmp:
            digests, out = os.path.join(tmp, "digests.txt"), os.path.join(tmp, "manifest.json")
            with open(digests, "w") as f:
                f.write("".join(line + "\n" for line in lines))
            p = subprocess.run([sys.executable, SCRIPT, version, commit, digests, out], capture_output=True, text=True)
            manifest = None
            if os.path.exists(out):
                with open(out) as f:
                    manifest = json.load(f)
            return p.returncode, p.stderr, manifest

    def every_image(self):
        return ["%s %s" % (a, digest(i + 1)) for i, a in enumerate(PUBLISHED)]

    def test_every_published_image_by_digest(self):
        code, err, manifest = self.run_with(self.every_image())
        self.assertEqual(code, 0, err)
        self.assertEqual(manifest["version"], VERSION)
        self.assertEqual(manifest["commit"], COMMIT)
        self.assertEqual(sorted(manifest["images"]), sorted(PUBLISHED))
        for i, a in enumerate(PUBLISHED):
            self.assertEqual(manifest["images"][a], "ghcr.io/otfabric/knx-interop-%s@%s" % (a, digest(i + 1)))
        xknx = re.search(r'^  xknx:\n(?:    .*\n)*?    version: "([^"]+)"', VERSIONS, re.M).group(1)
        self.assertEqual(manifest["upstream"]["xknx"]["version"], xknx)
        self.assertIn("revision", manifest["upstream"]["cbsigma"])
        self.assertNotIn("knxd", manifest["upstream"])

    def test_a_missing_digest_refuses_the_release(self):
        lines = self.every_image()
        left_out = lines.pop()
        code, err, manifest = self.run_with(lines)
        self.assertEqual(code, 1)
        self.assertIsNone(manifest)
        self.assertIn("no digest for %s, which versions.yaml publishes" % left_out.split()[0], err)

    def test_no_digests_refuse_the_release(self):
        code, err, manifest = self.run_with([])
        self.assertEqual(code, 1)
        self.assertIsNone(manifest)

    def test_an_unpublished_image_is_refused(self):
        code, err, _ = self.run_with(self.every_image() + ["knxd %s" % digest(99)])
        self.assertEqual(code, 1)
        self.assertIn("a digest for knxd, which versions.yaml does not publish", err)

    def test_a_malformed_or_repeated_digest_is_refused(self):
        lines = self.every_image()
        code, err, _ = self.run_with(lines[:-1] + [lines[-1].split()[0] + " sha256:abc"])
        self.assertEqual(code, 1)
        self.assertIn("not \"<adapter> sha256:<64 hex>\"", err)
        code, err, _ = self.run_with(lines + [lines[0]])
        self.assertEqual(code, 1)
        self.assertIn("two digests for %s" % lines[0].split()[0], err)

    def test_the_version_must_be_interop_version(self):
        code, err, _ = self.run_with(self.every_image(), version="v99.0.0")
        self.assertEqual(code, 1)
        self.assertIn("interop_version is not 99.0.0", err)


if __name__ == "__main__":
    unittest.main()
