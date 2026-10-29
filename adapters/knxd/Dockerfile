# SPDX-License-Identifier: MIT
# knxd 0.14.73-1 (GPL-2.0) from Debian trixie — https://github.com/knxd/knxd
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/debian:trixie-slim@sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4
ARG KNXD_VERSION=0.14.73-1
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends knxd=${KNXD_VERSION} knxd-tools=${KNXD_VERSION} gawk procps \
    && rm -rf /var/lib/apt/lists/* && knxd --version | head -1
COPY knxd/run.sh /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: knxd (Debian trixie package)" \
      org.opencontainers.image.licenses="MIT AND GPL-2.0-only"
ENTRYPOINT ["/adapter/run"]
