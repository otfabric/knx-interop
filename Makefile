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

ADAPTERS ?= goknx xknx knxultimate knxd calimero-server calimero-tools probe
# go-knx enters as an external, released input: the knxctl release
# KNXCTL_VERSION, installed in the goknx image. knx-interop never builds
# from go-knx or knxctl sources (go-knx and knxctl depend on knx-interop,
# not the other way round).
KNXCTL_VERSION ?= v0.5.0

image = $(REGISTRY)/knx-interop-$(1):$(VERSION)

.PHONY: help images image-% validate lint matrix matrix-quick capabilities release-notes

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_%-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

images: $(addprefix image-,$(ADAPTERS)) ## Build every adapter image for this machine's architecture

image-goknx:
	@echo "build $(call image,goknx) (knxctl $(KNXCTL_VERSION))"
	@docker build -q --build-arg BASE_REGISTRY=$(BASE_REGISTRY) --build-arg KNXCTL_VERSION=$(KNXCTL_VERSION) \
		-f adapters/goknx/Dockerfile -t $(call image,goknx) adapters >/dev/null

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

# GATE: fail only on failures that involve this adapter (go-knx, the
# implementation the matrix exists for); GATE= fails on any failure.
GATE ?= goknx
matrix: ## Run every scenario between every pair of adapters (Docker); writes reports/latest.{json,md}
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --gate "$(GATE)"

matrix-quick: ## Run the tunnel suite against the go-knx server and go-knx against the others
	@python3 scripts/run-matrix.py --registry $(REGISTRY) --version $(VERSION) --suites tunnel --report quick

release-notes: ## Print the release notes of VERSION from RELEASE.md
	@scripts/release-notes.sh $(VERSION)

