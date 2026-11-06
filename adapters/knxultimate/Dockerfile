# SPDX-License-Identifier: MIT
# KNXUltimate 6.3.2 (MIT) — https://github.com/Supergiovane/KNXUltimate
ARG BASE_REGISTRY=docker.io/library
FROM ${BASE_REGISTRY}/node:22-bookworm-slim@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d
WORKDIR /adapter
COPY knxultimate/package.json knxultimate/package-lock.json /adapter/
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force
COPY knxultimate/adapter.js /adapter/run
RUN chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: KNXUltimate 6.3.2" \
      org.opencontainers.image.licenses="MIT"
ENTRYPOINT ["/adapter/run"]
