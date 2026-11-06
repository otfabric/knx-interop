# SPDX-License-Identifier: MIT
# Self-documented Makefile (https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html)
# Run 'make' or 'make help' to list targets.

.DEFAULT_GOAL := help

REGISTRY ?= ghcr.io/otfabric
VERSION  ?= dev
PLATFORMS ?= linux/amd64,linux/arm64
# Registry of the base images (debian, python, node, golang), pinned by
# digest in the Dockerfiles; CI uses mirror.gcr.io/library (Docker Hub
# rate limits).
BASE_REGISTRY ?= docker.io/library

# The adapters: independent third-party stacks and the probe. A system
# under test is not part of this repository: it brings its own adapter image
# (ADAPTER=name=image, or ADAPTER_IMAGE_<name> with scripts/interop.sh).
ADAPTERS ?= xknx knxultimate knxd calimero-server calimero-tools probe
# The adapters a release publishes (.github/workflows/release.yml PUBLISHED):
# the others redistribute GPL binaries (THIRD_PARTY_NOTICES.md).
PUBLISHED_ADAPTERS ?= xknx knxultimate probe
ADAPTER ?=
export REGISTRY VERSION

image = $(REGISTRY)/knx-interop-$(1):$(VERSION)

# image-% and smoke-% are pattern rules, which make ignores for .PHONY
# targets: they depend on FORCE instead.
.PHONY: help all ci images validate lint smoke interop matrix matrix-quick capabilities print-adapters print-published-adapters release-notes fixture clean FORCE
FORCE:

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_%-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

all: validate images ## Validate and build the local images

ci: validate lint images smoke interop ## Full local CI: validate, lint, build, smoke and the cross-stack matrix
	@echo ""
	@echo "All local CI checks passed."

images: $(addprefix image-,$(ADAPTERS)) ## Build every adapter image for this machine's architecture

image-%: FORCE
	@echo "build $(call image,$*)"
	@docker build -q --build-arg BASE_REGISTRY=$(BASE_REGISTRY) -f adapters/$*/Dockerfile -t $(call image,$*) adapters >/dev/null

print-adapters: ## Print the adapter names
	@echo $(ADAPTERS)

print-published-adapters: ## Print the adapters a release publishes
	@echo $(PUBLISHED_ADAPTERS)

smoke: $(addprefix smoke-,$(ADAPTERS)) ## Container-contract smoke test of every image

smoke-%: FORCE ## Smoke test one adapter, e.g. smoke-xknx
	@scripts/smoke.sh $*

interop: ## Cross-stack matrix of ADAPTERS, each in the roles of its capabilities (reports/latest.*, reports/results.json)
	@scripts/interop.sh $(ADAPTERS)

capabilities: ## Print the capabilities document of every image
	@for a in $(ADAPTERS); do docker run --rm $(call image,$$a) capabilities; done

validate: ## Check versions.yaml against the Dockerfiles and the fixtures against their schema
	@python3 scripts/check-versions.py
	@python3 scripts/validate.py
	@python3 -m unittest discover -q -s scripts -p 'test_*.py'

lint: ## Shellcheck the shell adapters, byte-compile the Python ones, check the Node one
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s sh adapters/knxd/run.sh adapters/calimero-tools/run.sh adapters/calimero-server/run.sh && shellcheck -x -P scripts scripts/*.sh; else echo "(shellcheck not installed)"; fi
	@for f in adapters/*/*.py adapters/common/*.py scripts/*.py; do python3 -m py_compile $$f || exit 1; done
	@if command -v node >/dev/null 2>&1; then node --check adapters/knxultimate/adapter.js; fi

# GATE: fail only on failures that involve this adapter (a system under
# test); empty fails on any failure. ADAPTER adds an external adapter,
# name=image (a system under test with its own contract image), to the
# third-party matrix.
GATE ?=
matrix: ## Run every scenario between every pair of adapters (Docker); writes reports/latest.{json,md} and reports/results.json
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --gate "$(GATE)" $(if $(ADAPTER),--adapter $(ADAPTER))

matrix-quick: ## Run the tunnel suite only
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --suites tunnel --report quick $(if $(ADAPTER),--adapter $(ADAPTER))

fixture: ## Regenerate the KNX Secure test profile (adapters/common/secure) in the xknx image
	@docker run --rm -v $(CURDIR):/w -w /w --entrypoint python3 $(call image,xknx) scripts/secure-fixture.py adapters/common/secure

release-notes: ## Print the release notes of VERSION from RELEASE.md
	@scripts/release-notes.sh $(VERSION)

clean: ## Remove the generated reports
	@rm -f reports/*.results.json reports/results.json
