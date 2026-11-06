# SPDX-License-Identifier: MIT
# knxd 0.14.73-1 (GPL-2.0) from Debian trixie — https://github.com/knxd/knxd
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2
ARG KNXD_VERSION=0.14.73-1
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends knxd=${KNXD_VERSION} knxd-tools=${KNXD_VERSION} gawk procps \
    && rm -rf /var/lib/apt/lists/* && knxd --version | head -1
COPY knxd/run.sh /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: knxd (Debian trixie package)" \
      org.opencontainers.image.licenses="MIT AND GPL-2.0-only"
ENTRYPOINT ["/adapter/run"]
