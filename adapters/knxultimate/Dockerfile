# SPDX-License-Identifier: MIT
# KNXUltimate 6.3.1 (MIT) — https://github.com/Supergiovane/KNXUltimate
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/node:22-bookworm-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da
WORKDIR /adapter
COPY knxultimate/package.json knxultimate/package-lock.json /adapter/
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force
COPY knxultimate/adapter.js /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: KNXUltimate 6.3.1" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
