# SPDX-License-Identifier: MIT
# xknx 4.1.1 (MIT) — https://github.com/XKNX/xknx
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
COPY xknx/requirements.txt /adapter/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r /adapter/requirements.txt
COPY common/ /adapter/common/
COPY xknx/adapter.py /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: xknx 4.1.1" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
