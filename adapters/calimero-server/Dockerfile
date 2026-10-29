# SPDX-License-Identifier: MIT
# calimero-server 3.0-M1 (GPL-2.0 with the Classpath exception), the official
# multi-arch image pinned by digest — https://github.com/calimero-project
FROM calimeroproject/knxserver:3.0-M1@sha256:70463ad74c4c976cbc8c062fc219b19059f417562051670deeaa65c5e13f7f9c
COPY calimero-server/run.sh /adapter/run
COPY calimero-server/server-config.xml.in /adapter/server-config.xml.in
RUN echo "3.0-M1" > /adapter/VERSION && chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: calimero-server 3.0-M1" \
      org.opencontainers.image.licenses="MIT AND GPL-2.0-with-classpath-exception"
ENTRYPOINT ["/adapter/run"]
