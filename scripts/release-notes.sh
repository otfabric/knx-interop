#!/bin/sh
# SPDX-License-Identifier: MIT
# Print the RELEASE.md section of version $1 (vX.Y.Z or X.Y.Z), up to its
# closing "---" line.
set -eu
v=${1#v}
awk -v h="## v$v" '$0 == h {on=1; next} on && $0 == "---" {exit} on {print}' "$(dirname "$0")/../RELEASE.md"
