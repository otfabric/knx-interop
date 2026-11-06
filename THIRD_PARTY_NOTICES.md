# Third-party notices

The adapter scripts, runner, probe and fixtures of knx-interop are MIT
licensed ([LICENSE](LICENSE)). The images also contain third-party
software under its own licence, installed from upstream, unmodified:

| Image | Software | Licence | Source |
|---|---|---|---|
| knx-interop-calimero-server | calimero-server 3.0-M1 and its dependencies (the official image `calimeroproject/knxserver`) | GPL-2.0-only WITH Classpath-exception-2.0 | <https://github.com/calimero-project/calimero-server>, <https://github.com/calimero-project/calimero-core> |
| knx-interop-calimero-tools | calimero-tools 3.0-M1 (the official image `calimeroproject/knxtools`) | GPL-2.0-only WITH Classpath-exception-2.0 | <https://github.com/calimero-project/calimero-tools> |
| knx-interop-knxd | knxd and knxd-tools 0.14.73-1 (Debian trixie packages) | GPL-2.0-only | <https://github.com/knxd/knxd>, Debian source package `knxd` 0.14.73-1 |
| knx-interop-xknx | xknx 4.1.1 and its Python dependencies (cryptography, ifaddr) | MIT (xknx), Apache-2.0/BSD (cryptography), MIT (ifaddr) | <https://github.com/XKNX/xknx> |
| knx-interop-knxultimate | KNXUltimate 6.3.2 and its npm dependencies (package-lock.json) | MIT (KNXUltimate) and the licences of its dependencies | <https://github.com/Supergiovane/KNXUltimate> |
| knx-interop-cbsigma | cB-Sigma knx v0.2.0 and cB-Sigma knx-sim v0.2.0 (Go modules, linked into the MIT adapter `adapters/cbsigma/`; no other dependencies), the Go standard library | Apache-2.0 (knx, knx-sim; their LICENSE and NOTICE files are in the image under `/licenses`), BSD-3-Clause (Go) | <https://github.com/cB-Sigma/knx>, <https://github.com/cB-Sigma/knx-sim> |

## Image `knx-interop-otfabric`

OT Fabric's own stack (`own/go-knx/`), not part of a release: the adapter
(MIT) and the Go modules it is built from. Every module's licence text is in
the image under `/licenses` (`/licenses/BUNDLED-MODULES.txt` lists them with
their versions), with the KNX Secure test profile of this repository.

| Component | Version | Licence | Source |
|---|---|---|---|
| go-knx | latest release when built | MIT | <https://github.com/otfabric/go-knx> |
| Go standard library | the Go of the build image | BSD-3-Clause | <https://go.dev> |
| Adapter | this repository, `own/go-knx/` | MIT | <https://github.com/otfabric/knx-interop> |

Publishing policy (decided 2026-10-29): the release workflow publishes the
MIT images only (xknx, knxultimate, probe), and since v0.9.0 the cbsigma
image (MIT and Apache-2.0: Apache-2.0 allows redistribution with its
licence and NOTICE files, which the image carries). The images that contain GPL
binaries (calimero-server, calimero-tools, knxd) are never published: they
are built from their Dockerfiles wherever they are used (CI, `make
images`), from the upstream images and packages they pin.

KNX is a registered trademark of KNX Association cvba. knx-interop is not
affiliated with or endorsed by KNX Association.
