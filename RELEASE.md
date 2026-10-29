# knx-interop Releases

A release is a pushed tag `vX.Y.Z` equal to `interop_version` in
versions.yaml; the Release workflow builds the images and takes this
file's section of that version as the release notes. Add the section,
headed exactly `## vX.Y.Z` and closed by a line `---`, before tagging.

## v0.1.0

**Date:** 2026-10-29 (planned; not released)
**Previous release:** none

## Summary

The first set of adapters: Calimero server and tools 3.0-M1, knxd
0.14.73, xknx 4.0.0, KNXUltimate 6.3.1, go-knx (through knxctl) and a raw
KNXnet/IP probe, the container contract 1.0, the matrix runner with JSON
and Markdown reports, DPT fixtures and known differences.

---
