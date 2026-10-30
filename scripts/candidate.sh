#!/bin/sh
# SPDX-License-Identifier: MIT
# Build one adapter at a newer upstream release (a candidate) and run the
# whole matrix with it, gated on that adapter:
#
#   scripts/candidate.sh <adapter> <version>
#
# The pin is moved in the working tree only (Dockerfile, requirements.txt,
# package.json/package-lock.json), every image is built and
# `make matrix GATE=<adapter>` runs. Used by the Upstream workflow on a
# throwaway checkout; locally, `git checkout adapters/` undoes the edits.
# knxultimate needs npm on the host to update the lock file.
#
# Ends with "[candidate] <n> passed, <n> failed, ..." from reports/latest.json.
set -eu
cd "$(dirname "$0")/.."

adapter=${1:-}
version=${2:-}
if [ -z "$adapter" ] || [ -z "$version" ]; then
	echo "usage: candidate.sh calimero-server|calimero-tools|knxd|xknx|knxultimate <version>" >&2
	exit 2
fi

# edit FILE OLD NEW: replace the line matching OLD (an ERE) by NEW, once.
edit() {
	n=$(grep -cE "$2" "$1" || true)
	[ "$n" = 1 ] || { echo "candidate: $1 has $n lines matching $2" >&2; exit 1; }
	awk -v re="$2" -v new="$3" '$0 ~ re { print new; next } { print }' "$1" > "$1.tmp" && mv "$1.tmp" "$1"
}

case "$adapter" in
	calimero-server | calimero-tools)
		image=$([ "$adapter" = calimero-server ] && echo knxserver || echo knxtools)
		pin=$(sed -nE "s|^FROM calimeroproject/$image:([^@]+)@.*|\1|p" "adapters/$adapter/Dockerfile")
		edit "adapters/$adapter/Dockerfile" "^FROM calimeroproject/$image:" "FROM calimeroproject/$image:$version"
		edit "adapters/$adapter/Dockerfile" "^RUN echo \"$pin\" > /adapter/VERSION" \
			"$(grep "^RUN echo \"$pin\" > /adapter/VERSION" "adapters/$adapter/Dockerfile" | sed "s/\"$pin\"/\"$version\"/")"
		;;
	knxd)
		edit adapters/knxd/Dockerfile "^ARG KNXD_VERSION=" "ARG KNXD_VERSION=$version"
		;;
	xknx)
		edit adapters/xknx/requirements.txt "^xknx==" "xknx==$version"
		;;
	knxultimate)
		(cd adapters/knxultimate && npm install --package-lock-only --save-exact --no-audit --no-fund "knxultimate@$version")
		;;
	*)
		echo "candidate: unknown adapter $adapter" >&2
		exit 2
		;;
esac

git --no-pager diff --stat -- adapters/
make images
rc=0
make matrix GATE="$adapter" || rc=$?
python3 - "$adapter" <<'EOF'
import json, sys
doc = json.load(open("reports/latest.json"))
s = doc["summary"]
mine = [r for r in doc["results"] if r["status"] == "fail" and sys.argv[1] in (r["client"], r["peer"], r.get("observer"))]
print("[candidate] %d passed, %d failed (%d with %s), %d known-difference, %d unsupported, %d not-tested" % (
    s.get("pass", 0), s.get("fail", 0), len(mine), sys.argv[1], s.get("known-difference", 0),
    s.get("unsupported", 0), s.get("not-tested", 0)))
EOF
exit $rc
