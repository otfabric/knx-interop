#!/usr/bin/env bash
# Shared helpers for scripts/smoke.sh and scripts/interop.sh. Source, do not
# execute.
#
# The engines are scripts/smoke.py and scripts/run-matrix.py: servers and
# clients run as containers on a private Docker network, so no host port is
# published and parallel runs do not collide.

REGISTRY="${REGISTRY:-ghcr.io/otfabric}"
VERSION="${VERSION:-dev}"
export REGISTRY VERSION

log() { echo "[$(basename "$0" .sh)] $*" >&2; }

# image_of <adapter>: ADAPTER_IMAGE_<adapter> (a hyphen written as "_") names an
# image outside the release set, which this repository's scripts know nothing
# about. scripts/run-matrix.py reads the same variables.
image_of() {
    local override="ADAPTER_IMAGE_${1//-/_}"
    if [[ -n "${!override:-}" ]]; then echo "${!override}"; else echo "${REGISTRY}/knx-interop-$1:${VERSION}"; fi
}

require_tools() {
    local t
    for t in docker python3; do
        command -v "$t" >/dev/null || { log "missing required tool: $t"; exit 2; }
    done
}
