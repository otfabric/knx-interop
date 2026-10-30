# knx-interop Releases

A release is a pushed tag `vX.Y.Z` equal to `interop_version` in
versions.yaml; the Release workflow builds the images and takes this
file's section of that version as the release notes. Add the section,
headed exactly `## vX.Y.Z` and closed by a line `---`, before tagging.

## v0.6.0

**Date:** 2026-10-30
**Previous release:** v0.5.0

## Summary

Container contract 1.4: remote device management, plain and secured with
a device's tool key (KNX Data Secure point to point).

## Additions

- `remote-property` client operation: the remote property services
  (A_PropertyValue_Read, _Write) of a device through a tunnel,
  connectionless or in a transport connection (`--connected`), with the
  object found by its type in the device's interface object list.
  `--tool-access` secures the access with the device's tool key from the
  test profile (S-A_Sync, then S-A_Data with tool access).
- `server --tool-access`: the server's device accepts only management
  secured with its tool key.
- Capabilities `remoteProperty`, `toolAccess`, `server.remoteProperty`,
  `server.toolAccess`.
- `management` suite: per server and client, read, read in a connection
  and write (friendly name of the KNXnet/IP parameter object); with tool
  access the same, and the refusal of plain access by a secured device.
- Adapters: Calimero tools (`get -r`, `-c`, keyring tool key), xknx (its
  point-to-point management connection), Calimero server (its emulated
  device answers the remote property services; no tool key access).

## Notes

- Calimero tools 3.0-M1 computes the Data Secure MAC over the source
  address it sends, 0.0.0 unless set, while the tunnelling server
  replaces it by the tunnel address; the adapter sets the tunnel address
  (`-k 1.1.10`).

---

## v0.5.0

**Date:** 2026-10-30
**Previous release:** v0.4.0

## Summary

knx-interop holds third-party stacks only and depends on no system under
test.

## Changes

- The goknx adapter (knxctl) is removed, with its build from sibling go-knx
  and knxctl checkouts and the CI checkouts of their `main` branches.
- The runner takes external adapters: `--adapter name=image` (`make
  matrix ADAPTER=...`) adds a system under test that implements the
  container contract in an image of its own; it joins the roles of its
  capabilities and is preferred as observer and responder. go-knx runs
  the matrix this way from its own repository.
- Observers and responders default to third-party stacks (xknx, Calimero
  tools, KNXUltimate); the surrogate scenario of Calimero tools' Data
  Secure runs when a monitor offers the `surrogate` capability.
- The KNX Secure test profile is written by `scripts/secure-fixture.py`
  (Python, `make fixture`) instead of a Go tool importing go-knx; the
  profile is unchanged.
- `matrix-table.py` adds a column per external adapter.

---

## v0.4.0

**Date:** 2026-10-30
**Previous release:** v0.3.0

## Summary

Container contract 1.3: KNX IP Secure sessions over UDP, the servers'
secure routing, and Calimero tools' Data Secure through go-knx as the
surrogate.

## Additions

- `--udp` with `--secure` in the goknx and calimero-tools adapters (xknx:
  unsupported, its secure sessions are TCP only); `server --secure
  --routing` in the goknx and calimero-server adapters.
- The test profile: go-knx's routing source 15.15.255 is a device with a
  tool key, the only sender of the new Data Secure group 1/3/3; Calimero
  tools' tool key for 15.15.240.
- The `secure` suite: secure sessions over UDP (connect, write, read);
  each server's secure routing in from secure routers (seen through a
  secure tunnel) and out to them (from a secure tunnel); Calimero tools
  write Data Secure over secure routing through the surrogate.
- calimero-server 3.0-M1 secure routing: the adapter sets the latency
  tolerance and opens `io.calimero.knxnetip` to the server module (the
  official image fails with an IllegalAccessException otherwise).
- Known differences narrowed: Calimero tools' Data Secure through a tunnel
  (no surrogate there) and towards xknx alone (xknx is no surrogate).
- The goknx adapter builds knxctl v0.4.0 by default.

---

## v0.3.0

**Date:** 2026-10-30
**Previous release:** v0.2.0

## Summary

Container contract 1.2: KNX IP Secure and KNX Data Secure, with one public
test profile, in the adapters and in a new `secure` suite of the matrix.

## Additions

- The KNX Secure test profile in `adapters/common/secure` (keyring,
  Calimero keyfile, profile.json), written by `tools/secure-fixture` with
  go-knx v0.3.0 and copied into every adapter image. All values are public
  test values.
- `--secure` and `--user` in the goknx (knxctl keyring flags), xknx
  (`TUNNELING_TCP_SECURE`, `ROUTING_SECURE`, keyring for Data Secure) and
  calimero-tools (`--user`/`--device-key`, `--group-key`, `--keyring`)
  adapters; `server --secure` in the goknx (keyring host) and
  calimero-server (keyfile, tunnelling users) adapters.
- The `secure` suite: secure tunnelling against each secure server (bound
  user address, write, read, Data Secure through the tunnel, device
  management as user 1, plain connection refused) and secure routing with
  Data Secure between every pair of secure routers.
- A known difference: Calimero tools 3.0-M1 do not send Data Secure group
  telegrams with the profile (they need a "surrogate" and S-A_Sync).
- The matrix lets a read responder end by itself, so that a secure user's
  bound address is free for the next scenario.
- The goknx adapter builds knxctl v0.3.0 by default.

---

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
