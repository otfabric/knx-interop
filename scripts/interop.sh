#!/usr/bin/env bash
# Cross-stack test: the scenarios of scripts/run-matrix.py between the named
# adapters, each in the roles its capabilities declare.
#
# Usage: interop.sh <adapter> [<adapter> ...]      e.g. interop.sh xknx knxd calimero-server
#
# The probe checks every server's readiness and runs the negative suite; name
# it too (its image is needed either way). An adapter whose capabilities say
# upstream.independentEngine false is preferred as observer and responder.
# tests/known-differences.tsv lists the deviations of specific stacks; a case
# it explains is a known difference, never a pass.
#
# This tests the adapters against each other. It says nothing about any
# library that consumes the images.
#
# Environment: REGISTRY, VERSION (image tag, default dev), ADAPTER_IMAGE_<adapter>,
#              SUITES (comma-separated, default every suite), GATE (fail only on
#              failures that involve this adapter), REPORT (report name, default
#              latest: reports/latest.{json,md} and reports/results.json).
#              REPORT_DIR, when set, receives a copy of the reports.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=scripts/lib.sh
source "${SCRIPT_DIR}/lib.sh"

[[ $# -ge 1 ]] || { echo "usage: interop.sh <adapter> [<adapter> ...]" >&2; exit 2; }
require_tools
for adapter in "$@"; do
    export "ADAPTER_IMAGE_${adapter//-/_}=$(image_of "${adapter}")"
done
export "ADAPTER_IMAGE_probe=$(image_of probe)"
REPORT="${REPORT:-latest}"
args=(--adapters "$(IFS=,; echo "$*")" --report "${REPORT}" --gate "${GATE:-}")
[[ -n "${SUITES:-}" ]] && args+=(--suites "${SUITES}")
log "adapters: $* (${VERSION})"
python3 "${SCRIPT_DIR}/run-matrix.py" "${args[@]}"
rc=$?
if [[ -n "${REPORT_DIR:-}" ]]; then
    mkdir -p "${REPORT_DIR}"
    results="results.json"; [[ "${REPORT}" == latest ]] || results="${REPORT}.results.json"
    for f in "${REPORT}.json" "${REPORT}.md" "${results}"; do
        if [[ -f "${ROOT}/reports/${f}" && "$(cd "${REPORT_DIR}" && pwd)" != "${ROOT}/reports" ]]; then
            cp "${ROOT}/reports/${f}" "${REPORT_DIR}/"
        fi
    done
fi
exit "${rc}"
