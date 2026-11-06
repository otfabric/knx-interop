# SPDX-License-Identifier: MIT
# The knx-interop raw KNXnet/IP probe (Python standard library only).
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
COPY common/ /adapter/common/
COPY probe/probe.py /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop raw KNXnet/IP probe" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
