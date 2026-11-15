#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests of scripts/check-versions.py: it runs on a copy of the build inputs
with one value changed, and must fail with the reason."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# What check-versions.py reads.
FILES = ("versions.yaml", "RELEASE.md", "LICENSE", "Makefile", ".github/workflows/release.yml", "scripts/check-versions.py")
TREES = ("adapters", "own")


class CheckVersions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        for f in FILES:
            os.makedirs(os.path.dirname(os.path.join(self.tmp, f)), exist_ok=True)
            shutil.copy(os.path.join(ROOT, f), os.path.join(self.tmp, f))
        for t in TREES:
            shutil.copytree(os.path.join(ROOT, t), os.path.join(self.tmp, t))

    def edit(self, path, old, new, regex=False):
        p = os.path.join(self.tmp, path)
        with open(p) as f:
            text = f.read()
        if regex:
            text, n = re.subn(old, new, text, count=1, flags=re.M)
        else:
            n = text.count(old)
            text = text.replace(old, new, 1)
        self.assertGreaterEqual(n, 1, "%s: %r not found" % (path, old))
        with open(p, "w") as f:
            f.write(text)

    def check(self):
        p = subprocess.run([sys.executable, os.path.join(self.tmp, "scripts", "check-versions.py")],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def fails(self, *reasons):
        code, out = self.check()
        self.assertEqual(code, 1, out)
        for r in reasons:
            self.assertIn(r, out)

    def test_the_build_inputs_agree(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("versions.yaml agrees with the build inputs", out)

    def test_an_xknx_version_only_in_versions_yaml_fails(self):
        self.edit("versions.yaml", r'^(    version: )"4\.1\.1"', r'\1"4.1.2"', regex=True)
        self.fails("xknx: adapters/xknx/requirements.in does not pin versions.yaml's 4.1.2",
                   "requirements.txt locks xknx 4.1.1, versions.yaml says 4.1.2")

    def test_requirements_in_not_locked_fails(self):
        self.edit("versions.yaml", r'^(    version: )"4\.1\.1"', r'\1"4.1.2"', regex=True)
        self.edit("adapters/xknx/requirements.in", "xknx==4.1.1", "xknx==4.1.2")
        self.fails("requirements.txt does not lock xknx==4.1.2 (make lock-xknx)")

    def test_a_requirement_without_hashes_fails(self):
        self.edit("adapters/xknx/requirements.txt", r"^(ifaddr==\S+) \\\n(    --hash=\S+ \\\n)*    --hash=\S+\n", r"\1\n", regex=True)
        self.fails("not pinned with == and --hash=sha256: ifaddr==")

    def test_an_unpinned_requirement_fails(self):
        self.edit("adapters/xknx/requirements.txt", "ifaddr==", "ifaddr>=")
        self.fails("not pinned with == and --hash=sha256: ifaddr>=")

    def test_a_knxultimate_version_only_in_versions_yaml_fails(self):
        self.edit("versions.yaml", '"6.3.2"', '"6.3.3"')
        self.fails("knxultimate: package-lock.json does not install versions.yaml's 6.3.3",
                   "knxultimate: package.json does not pin versions.yaml's 6.3.3")

    def test_a_knxd_version_only_in_versions_yaml_fails(self):
        self.edit("versions.yaml", '"0.14.73-1"', '"0.14.75-1"')
        self.fails("knxd: the Dockerfile's KNXD_VERSION is not versions.yaml's 0.14.75-1")

    def test_a_calimero_tools_digest_only_in_versions_yaml_fails(self):
        self.edit("versions.yaml", "c83aa43c4a61f237104f08952d205cacab17d574040b46d5861b05cba4119966",
                  "0" * 64)
        self.fails("calimero-tools: the Dockerfile's FROM is not versions.yaml's image")

    def test_a_calimero_server_version_only_in_versions_yaml_fails(self):
        self.edit("versions.yaml", r'^(  calimero-server:\n(?:    .*\n)*?    version: )"3\.0-M1"', r'\1"3.0-M2"', regex=True)
        self.fails("calimero-server: versions.yaml's image calimeroproject/knxserver:3.0-M1@",
                   "calimero-server: the Dockerfile's /adapter/VERSION is not 3.0-M2")

    def test_published_must_be_what_the_release_publishes(self):
        self.edit("versions.yaml", r"^(  xknx:\n(?:    .*\n)*?    published: )true", r"\1false", regex=True)
        self.fails("published: versions.yaml says cbsigma knxultimate probe, release.yml PUBLISHED cbsigma knxultimate probe xknx",
                   "the Makefile's PUBLISHED_ADAPTERS cbsigma knxultimate probe xknx")

    def test_the_release_may_not_publish_more(self):
        self.edit(".github/workflows/release.yml", 'PUBLISHED: "xknx', 'PUBLISHED: "knxd xknx')
        self.fails("release.yml PUBLISHED cbsigma knxd knxultimate probe xknx")

    def test_an_implementation_without_published_fails(self):
        self.edit("versions.yaml", r"^(  probe:\n(?:    .*\n)*?)    published: true\n", r"\1", regex=True)
        self.fails("versions.yaml: probe has no published: true or false")

    def test_the_licence_copy_must_be_the_licence(self):
        self.edit("adapters/LICENSE", "MIT License", "MIT Licence")
        self.fails("adapters/LICENSE is not a copy of LICENSE")


if __name__ == "__main__":
    unittest.main()
