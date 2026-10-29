# SPDX-License-Identifier: MIT
# calimero-tools 3.0-M1 (GPL-2.0 with the Classpath exception), the official
# multi-arch image pinned by digest — https://github.com/calimero-project
FROM calimeroproject/knxtools:3.0-M1@sha256:c83aa43c4a61f237104f08952d205cacab17d574040b46d5861b05cba4119966
COPY common/secure/ /adapter/common/secure/
COPY calimero-tools/run.sh /adapter/run
RUN echo "3.0-M1" > /adapter/VERSION && chmod +x /adapter/run && /adapter/run capabilities
LABEL org.opencontainers.image.source="https://github.com/otfabric/knx-interop" \
      org.opencontainers.image.description="knx-interop adapter: calimero-tools 3.0-M1" \
      org.opencontainers.image.licenses="MIT AND GPL-2.0-with-classpath-exception"
ENTRYPOINT ["/adapter/run"]
