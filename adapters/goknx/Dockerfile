# SPDX-License-Identifier: MIT
# go-knx, the system under test, through knxctl (MIT): the released version
# KNXCTL_VERSION, an external input (knx-interop never builds go-knx or
# knxctl from source).
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/golang:1.25-bookworm@sha256:3b4a11519ad929d1e1d261a12cff056f0c85b735253d7d861346b9c6f8b36437 AS build
ARG KNXCTL_VERSION=v0.5.0
RUN CGO_ENABLED=0 GOBIN=/out go install github.com/otfabric/knxctl@${KNXCTL_VERSION}

FROM ${BASE_REGISTRY}/python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
COPY --from=build /out/knxctl /usr/local/bin/knxctl
COPY common/ /adapter/common/
COPY goknx/adapter.py /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: go-knx (knxctl)" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
