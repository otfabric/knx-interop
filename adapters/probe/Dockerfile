# SPDX-License-Identifier: MIT
# The knx-interop raw KNXnet/IP probe (Python standard library only).
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
COPY common/ /adapter/common/
COPY probe/probe.py /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop raw KNXnet/IP probe" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
