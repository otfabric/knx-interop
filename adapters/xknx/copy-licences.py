#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Copies the licence files of every distribution that requirements.txt pins
to <dest>/<name>/, in the image build (THIRD_PARTY_NOTICES.md):

    copy-licences.py <requirements.txt> <dest>

A distribution whose environment marker leaves it out on this Python is not
installed and is skipped. An installed one without a licence file in its
.dist-info fails the build."""

import importlib.metadata
import pathlib
import re
import shutil
import sys

LICENCE = re.compile(r"(^|/)(LICEN[CS]E|COPYING|NOTICE)[^/]*$", re.I)


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    requirements, dest = argv
    names = re.findall(r"^([A-Za-z0-9._-]+)==", pathlib.Path(requirements).read_text(), re.M)
    if not names:
        print("%s: no pinned requirement" % requirements, file=sys.stderr)
        return 1
    for name in names:
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            print("%s: not installed here (environment marker), skipped" % name)
            continue
        files = [f for f in dist.files or () if ".dist-info/" in str(f)
                 and LICENCE.search(str(f).split(".dist-info/", 1)[1])]
        if not files:
            print("%s %s: no licence file in its .dist-info" % (name, dist.version), file=sys.stderr)
            return 1
        out = pathlib.Path(dest, name)
        out.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copyfile(dist.locate_file(f), out / pathlib.PurePosixPath(str(f)).name)
        print("%s %s: %s" % (name, dist.version, ", ".join(sorted(pathlib.PurePosixPath(str(f)).name for f in files))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
