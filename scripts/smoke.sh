#!/usr/bin/env bash
# Container-contract smoke test for one adapter image.
#
# Usage: smoke.sh <adapter>          e.g. smoke.sh xknx
#
# Checks the parts of docs/CONTAINER_CONTRACT.md that need no second stack
# (the probe aside, which checks a server's readiness): the capabilities
# document, the KNX Secure test profile, usage errors, a server that answers
# a DESCRIPTION_REQUEST, a client operation that cannot reach its target and
# an operation the adapter does not offer (scripts/smoke.py).
#
# Environment: REGISTRY, VERSION (image tag, default dev), ADAPTER_IMAGE_<adapter>,
#              REPORT_DIR (keeps the capabilities document when set).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "${SCRIPT_DIR}/lib.sh"

ADAPTER="${1:?usage: smoke.sh ADAPTER}"
require_tools
IMAGE="$(image_of "${ADAPTER}")"
log "${IMAGE}"
exec python3 "${SCRIPT_DIR}/smoke.py" "${ADAPTER}" "${IMAGE}" "$(image_of probe)"
