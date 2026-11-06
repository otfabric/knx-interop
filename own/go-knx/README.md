# knx-interop-otfabric

[go-knx](https://github.com/otfabric/go-knx), OT Fabric's own KNX stack,
behind the [container contract](../../docs/CONTAINER_CONTRACT.md), so that
other stacks can test against it. Anything that uses a
`knx-interop-<adapter>` image can use this one in its place. Unlike those, it
is not a reference: its tags are go-knx versions, and no harness release
contains it.

**For testing only.** It runs an unauthenticated KNXnet/IP server, and its
KNX Secure mode uses the public test profile of this repository
(`adapters/common/secure`, every key and password published). Do not expose
it to a network you do not control. Old images stay available, so check
[go-knx advisories](https://github.com/otfabric/go-knx/security/advisories)
for the version you pull.

**Not an independent implementation.** The image declares
`upstream.independentEngine: false`, and `results.json` records
`independent: false`. A result against it says nothing independent about
go-knx when OT Fabric produces it. A result you publish, naming the
implementation and version, is independent evidence, and we would like to
hear about it.

## Use

```sh
docker network create knx
docker run -d --name go-knx --network knx ghcr.io/otfabric/knx-interop-otfabric:<tag> server --routing
docker run --rm --network knx ghcr.io/otfabric/knx-interop-xknx:<harness version> client read --target go-knx --group 1/0/2 --dpt 9.001
```

The server prints `READY` on stderr once it listens; a client waits until
its DESCRIPTION_REQUEST is answered (the contract). Multicast discovery and
routing need every participant on one Docker network.

`<tag>` is a go-knx version such as `v0.7.0`, or `latest`, the newest one
published. A rebuild of a version replaces its tag, so pin the digest if you
need an exact build. The digest is in the summary of the
[workflow run](https://github.com/otfabric/knx-interop/actions/workflows/own-go-knx.yml),
and `docker run --rm <image> capabilities` prints the versions (`upstream`,
`adapterVersion`).

| | |
|---|---|
| Upstream | go-knx, the latest release when the image was built |
| Licence | MIT; every module's licence is in the image under `/licenses` |
| Adapter name | `otfabric` (the name in documents) |
| Roles | server (tunnelling UDP and TCP, routing, KNX IP Secure, device management, busmonitor, remote management with tool access), client (every contract operation except the probe's `negative`) |
| Language | Go |
| Protocol engine | OT Fabric's own |

## Why it is apart from the other adapters

`REQUIREMENTS.md` R1: nothing under `adapters/`, `fixtures/`, `schemas/`,
`scenarios/`, `scripts/`, `tests/`, the top-level `Makefile` or
`compose.yaml` knows a library under test, and CI enforces that. This
directory and `.github/workflows/own-go-knx.yml` are the one exception. The
scripts take the image through `ADAPTER_IMAGE_otfabric`.

No release loop can form (`otfabric/engineering` ADR-0012). This image is
built by hand, from the latest go-knx release, and nothing is committed: this
repository has no pin of go-knx to bump. No release or required check of
go-knx needs the image, and go-knx commits no pin of it. It is not in a
harness release.

## Publishing

Run the **Own stack (go-knx)** workflow by hand, from `main`. It finds the
latest go-knx release and the latest harness release, and prints them. It
builds the image, runs the smoke test and the cross-stack self-test on both
architectures, then publishes `:<go-knx version>` and `:latest`. Run from a
branch, it stops before publishing. Nothing runs it automatically, so after
a go-knx release the image stays on the old version until someone does.

The workflow tests against the published references only: xknx,
KNXUltimate, cB-Sigma knx (with knx-sim, the sim suite) and the probe.
The images with GPL binaries (knxd, Calimero) are
never published ([THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)), so
there it has no third-party server. Locally, build them and run the whole
matrix with it:

```sh
make -f own/go-knx/Makefile image smoke interop                 # from the repository root, published references
make images                                                      # every reference as :dev
ADAPTER_IMAGE_otfabric=ghcr.io/otfabric/knx-interop-otfabric:dev VERSION=dev \
  scripts/interop.sh otfabric xknx knxultimate knxd calimero-server calimero-tools cbsigma probe
```

## What it cannot do

Nothing in the contract is declared `false`: go-knx's public API offers
every operation the contract has for a client and a server, apart from the
probe's `negative` (hand-built malformed datagrams), which answers
`unsupported`. The server is a simulator: a virtual device with the group
objects of the contract, and busmonitor connections that coexist with
tunnels.
