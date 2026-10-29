# Third-party notices

The adapter scripts, runner, probe and fixtures of knx-interop are MIT
licensed ([LICENSE](LICENSE)). The images also contain third-party
software under its own licence, installed from upstream, unmodified:

| Image | Software | Licence | Source |
|---|---|---|---|
| knx-interop-calimero-server | calimero-server 3.0-M1 and its dependencies (the official image `calimeroproject/knxserver`) | GPL-2.0-only WITH Classpath-exception-2.0 | <https://github.com/calimero-project/calimero-server>, <https://github.com/calimero-project/calimero-core> |
| knx-interop-calimero-tools | calimero-tools 3.0-M1 (the official image `calimeroproject/knxtools`) | GPL-2.0-only WITH Classpath-exception-2.0 | <https://github.com/calimero-project/calimero-tools> |
| knx-interop-knxd | knxd and knxd-tools 0.14.73-1 (Debian trixie packages) | GPL-2.0-only | <https://github.com/knxd/knxd>, Debian source package `knxd` 0.14.73-1 |
| knx-interop-xknx | xknx 4.0.0 and its Python dependencies (cryptography, ifaddr) | MIT (xknx), Apache-2.0/BSD (cryptography), MIT (ifaddr) | <https://github.com/XKNX/xknx> |
| knx-interop-knxultimate | KNXUltimate 6.3.1 and its npm dependencies (package-lock.json) | MIT (KNXUltimate) and the licences of its dependencies | <https://github.com/Supergiovane/KNXUltimate> |
| knx-interop-goknx | knxctl and go-knx | MIT | <https://github.com/otfabric/knxctl>, <https://github.com/otfabric/go-knx> |

Publishing policy (decided 2026-10-29): the release workflow publishes the
MIT images only (xknx, knxultimate, probe). The images that contain GPL
binaries (calimero-server, calimero-tools, knxd) are never published: they
are built from their Dockerfiles wherever they are used (CI, `make
images`), from the upstream images and packages they pin.

KNX is a registered trademark of KNX Association cvba. knx-interop is not
affiliated with or endorsed by KNX Association.
