# Capabilities

What each adapter declares in its `capabilities` document (contract 1.6,
[CONTAINER_CONTRACT.md](CONTAINER_CONTRACT.md)), as built from this
repository (`otfabric`: go-knx v0.8.0, the release it was last built
from). A scenario that needs a feature declared `no` is `unsupported`, never
a pass; – means the adapter does not declare the feature (the runner reads
those it needs, as the contract lists them). `otfabric` is OT Fabric's own go-knx
([own/go-knx/README.md](../own/go-knx/README.md)): not a reference, and the
only adapter with `upstream.independentEngine: false`.

Print them with `make capabilities` (and `docker run --rm <image> capabilities`).

## Roles

| Adapter | Implementation | Version | Roles | Independent engine |
|---|---|---|---|---|
| `calimero-server` | calimero-server | 3.0-M1 | server | yes |
| `calimero-tools` | calimero | 3.0-M1 | client | yes |
| `knxd` | knxd | 0.14.73 | server, client | yes |
| `xknx` | xknx | 4.1.1 | client | yes |
| `knxultimate` | knxultimate | 6.3.2 | client | yes |
| `cbsigma` | cbsigma (cB-Sigma knx) | v0.2.0 | client | yes |
| `probe` | probe | 1.0 | client | yes |
| `otfabric` | go-knx | v0.8.0 | server, client | no |

## Client features

| Feature | `calimero-tools` | `knxd` | `xknx` | `cbsigma` | `knxultimate` | `probe` | `otfabric` |
|---|---|---|---|---|---|---|---|
| `discover` | yes | no | yes | yes | yes | – | yes |
| `describe` | yes | no | yes | yes | yes | yes | yes |
| `connect` | yes | yes | – | – | yes | – | – |
| `tunnel` | yes | yes | yes | yes | yes | – | yes |
| `nat` | yes | yes | yes | yes | no | – | yes |
| `routing` | yes | yes | yes | yes | yes | – | yes |
| `answer` | no | yes | yes | yes | yes | – | yes |
| `dptCodec` | yes | no | – | – | yes | – | – |
| `tcp` | yes | no | yes | yes | yes | – | yes |
| `property` | yes | no | no | no | no | – | yes |
| `busmonitor` | yes | no | no | yes | no | – | yes |
| `secure` | yes | no | yes | yes | no | – | yes |
| `dataSecure` | yes | – | yes | yes | – | – | yes |
| `secureUdp` | yes | – | – | no | – | – | yes |
| `surrogate` | – | – | – | no | – | – | yes |
| `remoteProperty` | yes | – | yes | no | – | – | yes |
| `toolAccess` | yes | – | no | no | – | – | yes |
| `keyring` (1.6) | – | – | – | yes | – | – | yes |

## Server features (`features.server`)

| Feature | `calimero-server` | `knxd` | `otfabric` |
|---|---|---|---|
| `tcp` | yes | no | yes |
| `property` | yes | no | yes |
| `busmonitor` | no | yes | yes |
| `secure` | yes | – | yes |
| `secureUdp` | yes | – | yes |
| `secureRouting` | yes | – | yes |
| `remoteProperty` | yes | – | yes |
| `toolAccess` | no | – | yes |

cbsigma's image also runs cB-Sigma knx-sim (`sim`, `sim-ctl`, `sim-keyring`)
for the sim and files suites; that is not a contract role, and the image
declares no server features.

The probe declares `describe` and `negative` only (malformed datagrams
against each server). Server routing (`--routing`) is the client feature
`routing` of the same image, where it has both roles; calimero-server
routes as a server only (`features.routing`).
