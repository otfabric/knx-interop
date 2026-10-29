# SPDX-License-Identifier: MIT
# xknx 4.0.0 (MIT) — https://github.com/XKNX/xknx
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
COPY xknx/requirements.txt /adapter/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r /adapter/requirements.txt
COPY common/ /adapter/common/
COPY xknx/adapter.py /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: xknx 4.0.0" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
