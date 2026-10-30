# knx-interop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI Status](https://github.com/otfabric/knx-interop/actions/workflows/ci.yml/badge.svg)](https://github.com/otfabric/knx-interop/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/otfabric/knx-interop?label=release)](https://github.com/otfabric/knx-interop/releases)

Interoperability tests for KNX over KNXnet/IP between independent
implementations, run headless in containers on an isolated Docker network:
[Calimero](https://github.com/calimero-project) (Java),
[knxd](https://github.com/knxd/knxd) (C++), [xknx](https://github.com/XKNX/xknx)
(Python), [KNXUltimate](https://github.com/Supergiovane/KNXUltimate)
(TypeScript), plus a raw KNXnet/IP probe for negative tests. Part of
[OT Fabric](https://otfabric.io).

The repository holds third-party stacks only. A system under test brings
its own adapter image, built from its own sources, and runs this matrix
with it (`--adapter name=image`): [go-knx](https://github.com/otfabric/go-knx)
does so in its interop suite. knx-interop depends on no system under test;
they depend on it.

Results: [docs/INTEROPERABILITY.md](docs/INTEROPERABILITY.md) and
`reports/latest.{json,md}`.

## What is tested

Every client adapter against every server adapter, and every routing
adapter against every other:

| Suite | Scenarios |
|---|---|
| tunnel | multicast discovery, description, connect/disconnect, group write (seen by an independent observer), group read answered by an independent responder |
| dpt | twelve datapoint values (DPT 1, 5, 7, 9, 12, 13, 14, 16) written by one implementation and decoded octet for octet by another, against fixtures recomputed from the encoding rules |
| negative | the probe against each server: malformed headers, lengths, HPAIs and CRIs; unknown service types; status codes for unknown channels and connection types; duplicate and out-of-order sequence numbers; sequence roll-over; channel exhaustion |
| routing | a routing indication written by one implementation and received by another on 224.0.23.12:3671 |
| v2 | group write and read over TCP (KNXnet/IP core v2); device management (M_PropRead of the device serial number); a busmonitor connection that sees another client's write |
| secure | KNX IP Secure tunnelling against each secure server over TCP and UDP (session with a bound user address, write, read, Data Secure group write through the tunnel, device management as the management user, refusal of plain connections); secure routing and Data Secure over secure routing between every pair of secure routers (Calimero tools through go-knx as the surrogate); each server's secure routing, in from and out to secure routers. All with the public test profile in [adapters/common/secure](adapters/common/secure) |
| management | remote device management of each server's device (1.1.0) through a tunnel: property read connectionless and in a transport connection, property write read back; with tool access (KNX Data Secure point to point with the device's tool key, after S-A_Sync) the same, and plain access refused by the secured device |

Results are `pass`, `fail`, `unsupported` (the adapter or stack does not
offer the operation), `not-tested` (a prerequisite failed) or
`known-difference` (a verified deviation listed in
[tests/known-differences.tsv](tests/known-differences.tsv) with its
evidence). Each result records the implementations and versions.

## Adapters

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| `calimero-server` | Calimero KNXnet/IP server, emulated subnet | 3.0-M1 (official image, pinned by digest) | server |
| `calimero-tools` | Calimero tools | 3.0-M1 (official image, pinned by digest) | client |
| `knxd` | knxd and knxtool, dummy bus | 0.14.73-1 (Debian trixie) | server, client |
| `xknx` | xknx | 4.0.0 | client |
| `knxultimate` | KNXUltimate | 6.3.1 | client |
| `probe` | hand-built datagrams (Python standard library) | 1.0 | negative tests |

How each was chosen, and the rejected candidates (openHAB embeds Calimero):
[docs/CANDIDATES.md](docs/CANDIDATES.md). Versions and digests:
[versions.yaml](versions.yaml). The container contract:
[docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md).

## Running

Docker (Docker Desktop on macOS works) and Python 3.

```bash
make images                         # build every adapter image
make matrix                         # every suite, every pair: reports/latest.{json,md}
make matrix ADAPTER=sut=my/image:tag GATE=sut   # with a system under test, gating on it
python3 scripts/run-matrix.py --servers calimero-server --clients xknx,calimero-tools --suites tunnel
```

A system under test's adapter implements the container contract
([docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md)) and joins every
role its capabilities declare; it is preferred as observer and responder.

One scenario by hand:

```bash
docker network create knx
docker run -d --name srv --network knx ghcr.io/otfabric/knx-interop-calimero-server:dev server
docker run --rm --network knx ghcr.io/otfabric/knx-interop-xknx:dev client read --target srv --group 1/0/2 --dpt 9.001
```

## CI

`.github/workflows/ci.yml` lints the adapters, validates fixtures and
versions, builds every image natively on amd64 and arm64 GitHub runners,
and runs the whole matrix (multicast works on a user-defined bridge
network on hosted runners), uploading the reports. It runs on every push,
weekly, and on demand. Releases are
tag-driven ([RELEASE.md](RELEASE.md)).

`.github/workflows/upstream.yml` compares every pin with the latest
upstream release every day (`scripts/latest-upstream.py`: the Calimero
images on Docker Hub, knxd in Debian trixie, xknx on PyPI, KNXUltimate on
npm) and checks whether the tag of every
digest-pinned base image has moved. An adapter that is behind is built at
the latest release and the whole matrix runs with it
(`scripts/candidate.sh <adapter> <version>`). While a pin is behind, an issue
holds the table; it is closed once every pin is current again. Pins only
move by a reviewed change.

## Known limitations

- Multicast discovery and routing need all participants on one Docker
  network; hosts outside it are not reached.
- The knxd Debian package has no search or description tools.
- The KNX Secure scenarios use one test profile (keyring, keyfile); keys
  of real installations are never needed or used. KNXUltimate and knxd are
  not in the secure suite (their adapters do not configure security); xknx
  runs secure sessions over TCP only.
- Calimero tools send Data Secure group telegrams only through a surrogate
  device; none of the third-party stacks acts as one, so that scenario
  needs a system under test that does (see the known differences).
- calimero-server 3.0-M2 has no image; 3.0-M1 is used.
- Remote device management: knxd and KNXUltimate take no part (their
  adapters do not drive it); xknx manages devices only in transport
  connections and without tool keys; Calimero server's emulated device has
  no tool key access, so the tool access scenarios need a system under test
  as the device.

## License

MIT for this repository; the images contain third-party software under its
own licence ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). KNX is a
registered trademark of KNX Association cvba; knx-interop is not affiliated
with or endorsed by KNX Association.
