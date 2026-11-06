# SPDX-License-Identifier: MIT
#
# knx-interop adapter for cB-Sigma knx v0.2.0 and knx-sim v0.2.0 (both
# Apache-2.0) — https://github.com/cB-Sigma/knx, https://github.com/cB-Sigma/knx-sim
#
# Build from the repository root (the build context is adapters/):
#   make image-cbsigma
#
# The pins are go.mod and go.sum here, mirrored by the ARGs below and by
# versions.yaml (scripts/check-versions.py). "scripts/candidate.sh cbsigma
# <version>" moves both modules to another release in the working tree.
# The adapter is MIT and links them statically; the image carries their
# LICENSE and NOTICE files under /licenses.

ARG BASE_REGISTRY=docker.io/library
ARG GOLANG_DIGEST=sha256:e58d6f83b3416618d8bcac2b3dde1b7f7e3c4a77d25e88637f8bbae81536c48d
ARG DEBIAN_DIGEST=sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2

FROM ${BASE_REGISTRY}/golang:1.27.2-trixie@${GOLANG_DIGEST} AS build

# The commits of the release tags (go.mod pins the versions).
ARG UPSTREAM_SHA=8221e2fd1bdcefffd06344e0718d51f272fd13eb
ARG SIM_SHA=c30a0f175db896b36db0eb1fd76be2862b4379d1

ENV CGO_ENABLED=0 GOFLAGS=-mod=readonly GOTOOLCHAIN=local
WORKDIR /src
COPY cbsigma/go.mod cbsigma/go.sum ./
RUN go mod download && go mod verify
COPY cbsigma/*.go ./
RUN test -z "$(gofmt -l .)" \
    && go vet ./... \
    && go build -trimpath -ldflags "-s -w \
         -X main.upstreamRevision=${UPSTREAM_SHA} \
         -X main.simRevision=${SIM_SHA}" \
         -o /out/run . \
    && mkdir -p /out/licenses/knx /out/licenses/knx-sim /out/licenses/go \
    && cp "$(go list -m -f '{{.Dir}}' github.com/cB-Sigma/knx)/LICENSE" \
          "$(go list -m -f '{{.Dir}}' github.com/cB-Sigma/knx)/NOTICE" /out/licenses/knx/ \
    && cp "$(go list -m -f '{{.Dir}}' github.com/cB-Sigma/knx-sim)/LICENSE" \
          "$(go list -m -f '{{.Dir}}' github.com/cB-Sigma/knx-sim)/NOTICE" /out/licenses/knx-sim/ \
    && cp "$(go env GOROOT)/LICENSE" /out/licenses/go/LICENSE

FROM ${BASE_REGISTRY}/debian:trixie-slim@${DEBIAN_DIGEST}
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin interop
COPY --from=build /out/run /adapter/run
COPY --from=build /out/licenses /licenses
# The KNX Secure test profile of the contract (public test values).
COPY common/ /adapter/common/
RUN /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: cB-Sigma knx v0.2.0 and knx-sim v0.2.0" \
      org.opencontainers.image.licenses="MIT AND Apache-2.0"
USER interop
ENTRYPOINT ["/adapter/run"]
