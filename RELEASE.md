# knx-interop Releases

A release is a pushed tag `vX.Y.Z` equal to `interop_version` in
versions.yaml; the Release workflow builds the images and takes this
file's section of that version as the release notes. Add the section,
headed exactly `## vX.Y.Z` and closed by a line `---`, before tagging.

## v0.2.0

**Date:** 2026-10-29
**Previous release:** v0.1.0

## Summary

Container contract 1.1: tunnelling over TCP, device management and
busmonitor, in the adapters and in a new `v2` suite of the matrix.

## Additions

- `--tcp` in the calimero-tools, xknx (TUNNELING_TCP), KNXUltimate
  (TunnelTCP) and goknx adapters.
- `property` (M_PropRead) in the calimero-tools (`get --local`) and goknx
  adapters; `busmonitor` in the calimero-tools (`monitor`) and goknx
  adapters.
- `server` capabilities: TCP, device management and busmonitor of
  calimero-server, knxd and go-knx.
- The goknx adapter builds knxctl v0.2.0 by default.

---

## v0.1.0

**Date:** 2026-10-29
**Previous release:** none

## Summary

The first set of adapters: Calimero server and tools 3.0-M1, knxd
0.14.73, xknx 4.0.0, KNXUltimate 6.3.1, go-knx (through knxctl) and a raw
KNXnet/IP probe, the container contract 1.0, the matrix runner with JSON
and Markdown reports, DPT fixtures and known differences. Matrix: 336
pass, 5 known differences, 6 unsupported, 0 fail. Upstream reports:
KNXUltimate#117, calimero-tools#24, knxd#667.

Published images (MIT): knx-interop-xknx, knx-interop-knxultimate,
knx-interop-probe. The images with GPL binaries are built when needed.

---
