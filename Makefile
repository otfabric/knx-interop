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
# under test (go-knx) is not part of this repository: it brings its own
# adapter image and runs the matrix with ADAPTER=name=image.
ADAPTERS ?= xknx knxultimate knxd calimero-server calimero-tools probe
ADAPTER ?=

image = $(REGISTRY)/knx-interop-$(1):$(VERSION)

.PHONY: help images image-% validate lint matrix matrix-quick capabilities release-notes fixture

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_%-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

images: $(addprefix image-,$(ADAPTERS)) ## Build every adapter image for this machine's architecture

image-%:
	@echo "build $(call image,$*)"
	@docker build -q --build-arg BASE_REGISTRY=$(BASE_REGISTRY) -f adapters/$*/Dockerfile -t $(call image,$*) adapters >/dev/null

capabilities: ## Print the capabilities document of every image
	@for a in $(ADAPTERS); do docker run --rm $(call image,$$a) capabilities; done

validate: ## Check versions.yaml against the Dockerfiles and the fixtures against their schema
	@python3 scripts/check-versions.py
	@python3 scripts/validate.py

lint: ## Shellcheck the shell adapters, byte-compile the Python ones, check the Node one
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s sh adapters/knxd/run.sh adapters/calimero-tools/run.sh adapters/calimero-server/run.sh; else echo "(shellcheck not installed)"; fi
	@for f in adapters/*/*.py adapters/common/*.py scripts/*.py; do python3 -m py_compile $$f || exit 1; done
	@if command -v node >/dev/null 2>&1; then node --check adapters/knxultimate/adapter.js; fi

# GATE: fail only on failures that involve this adapter (a system under
# test); empty fails on any failure. ADAPTER adds an external adapter,
# name=image (a system under test with its own contract image).
GATE ?=
matrix: ## Run every scenario between every pair of adapters (Docker); writes reports/latest.{json,md}
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --gate "$(GATE)" $(if $(ADAPTER),--adapter $(ADAPTER))

matrix-quick: ## Run the tunnel suite only
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --suites tunnel --report quick $(if $(ADAPTER),--adapter $(ADAPTER))

fixture: ## Regenerate the KNX Secure test profile (adapters/common/secure) in the xknx image
	@docker run --rm -v $(CURDIR):/w -w /w --entrypoint python3 $(call image,xknx) scripts/secure-fixture.py adapters/common/secure

release-notes: ## Print the release notes of VERSION from RELEASE.md
	@scripts/release-notes.sh $(VERSION)

