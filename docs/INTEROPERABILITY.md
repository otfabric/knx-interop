# Interoperability matrix

Run of 2026-10-30 on Docker Desktop (macOS, arm64), report
[reports/latest.json](../reports/latest.json) /
[reports/latest.md](../reports/latest.md): **423 pass, 7 known
differences, 58 unsupported, 0 fail** (488 results). Each cell counts the
results in which that implementation took the role named in the row (every
pairing with every other implementation; go-knx is in most cells as a peer
or an observer).

Versions: calimero-server and calimero-tools 3.0-M1 (official images,
pinned by digest), knxd 0.14.73-1 (Debian trixie), xknx 4.0.0, KNXUltimate
6.3.1, go-knx v0.4.0 through knxctl v0.4.0, probe 1.0.

| Feature | calimero | knxd | xknx | KNXUltimate | go-knx |
|---|---|---|---|---|---|
| Discovery (as client) | PASS (3) | UNSUPPORTED 3 | PASS (3) | PASS (3) | PASS (3) |
| Description (as client) | PASS (3) | UNSUPPORTED 3 | PASS (3) | KNOWN DIFFERENCE 2, PASS 1 | PASS (3) |
| Tunnelling client | PASS (3) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| Tunnelling server | PASS (10) | PASS (10) | NOT TESTED | NOT TESTED | PASS (10) |
| Group write | PASS 5, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 3 | PASS 5, UNSUPPORTED 1 | PASS 5, UNSUPPORTED 1 | PASS 5, UNSUPPORTED 1 |
| Group read (client) | PASS 5, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 3 | PASS 5, UNSUPPORTED 1 | PASS 5, UNSUPPORTED 1 | PASS 5, UNSUPPORTED 1 |
| Group response (responder/observer) | NOT TESTED | NOT TESTED | PASS (18) | NOT TESTED | PASS (5) |
| Routing (sender) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| Routing (receiver) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| DPT encoding (sender) | PASS (36) | PASS (36) | PASS (36) | PASS (36) | PASS (36) |
| DPT decoding (observer) | NOT TESTED | NOT TESTED | PASS (36) | NOT TESTED | PASS (144) |
| Negative tests (server) | KNOWN DIFFERENCE 2, PASS 22 | PASS (24) | NOT TESTED | NOT TESTED | PASS (24) |
| Tunnelling over TCP (client) | PASS 4, UNSUPPORTED 2 | UNSUPPORTED 6 | PASS 4, UNSUPPORTED 2 | PASS 4, UNSUPPORTED 2 | PASS 4, UNSUPPORTED 2 |
| Tunnelling over TCP (server) | PASS 8, UNSUPPORTED 2 | UNSUPPORTED 10 | NOT TESTED | NOT TESTED | PASS 8, UNSUPPORTED 2 |
| Device management (client) | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 3 | UNSUPPORTED 3 | UNSUPPORTED 3 | PASS 2, UNSUPPORTED 1 |
| Device management (server) | PASS 2, UNSUPPORTED 3 | UNSUPPORTED 5 | NOT TESTED | NOT TESTED | PASS 2, UNSUPPORTED 3 |
| Busmonitor (client) | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 3 | UNSUPPORTED 3 | UNSUPPORTED 3 | PASS 2, UNSUPPORTED 1 |
| Busmonitor (server) | UNSUPPORTED 5 | PASS 2, UNSUPPORTED 3 | NOT TESTED | NOT TESTED | PASS 2, UNSUPPORTED 3 |
| IP Secure tunnelling (client) | PASS (6) | UNSUPPORTED 2 | PASS (6) | UNSUPPORTED 2 | PASS (6) |
| IP Secure tunnelling (server) | PASS 10, UNSUPPORTED 2 | UNSUPPORTED 1 | NOT TESTED | NOT TESTED | PASS 10, UNSUPPORTED 2 |
| IP Secure sessions over UDP (client) | PASS (6) | NOT TESTED | UNSUPPORTED 6 | NOT TESTED | PASS (6) |
| IP Secure sessions over UDP (server) | PASS 6, UNSUPPORTED 3 | NOT TESTED | NOT TESTED | NOT TESTED | PASS 6, UNSUPPORTED 3 |
| IP Secure device management (client) | PASS (2) | NOT TESTED | UNSUPPORTED 2 | NOT TESTED | PASS (2) |
| IP Secure device management (server) | PASS 2, UNSUPPORTED 1 | NOT TESTED | NOT TESTED | NOT TESTED | PASS 2, UNSUPPORTED 1 |
| IP Secure routing (sender) | PASS (2) | UNSUPPORTED 1 | PASS (2) | UNSUPPORTED 1 | PASS (2) |
| IP Secure routing (receiver) | PASS (2) | NOT TESTED | PASS (2) | NOT TESTED | PASS (2) |
| IP Secure routing (server) | PASS (6) | NOT TESTED | NOT TESTED | NOT TESTED | PASS (5) |
| Data Secure (sender) | KNOWN DIFFERENCE 3, PASS 1 | NOT TESTED | PASS (4) | NOT TESTED | PASS (4) |
| Data Secure (receiver) | PASS (2) | NOT TESTED | KNOWN DIFFERENCE 1, PASS 3 | NOT TESTED | KNOWN DIFFERENCE 2, PASS 4 |

Legend: PASS, FAIL, UNSUPPORTED (the stack or its adapter does not offer
it), NOT TESTED (no scenario uses the implementation in that role yet),
KNOWN DIFFERENCE (a verified deviation, below). HARDWARE REQUIRED and
BLOCKED do not occur in this run: nothing needs hardware. The secure rows
use the public test profile of contract 1.2; KNXUltimate and knxd take no
part in them.

## Bidirectional coverage

| Direction | Scenarios that pass |
|---|---|
| go-knx client → Calimero server | discovery, description, connect, write, read, 12 DPT vectors |
| go-knx client → knxd server | discovery, description, connect, write, read (answered by xknx through knxd), 12 DPT vectors |
| Calimero tools → go-knx server | discovery, description, connect, write, read, 12 DPT vectors |
| xknx → go-knx server | discovery, description, connect, write, read, 12 DPT vectors |
| KNXUltimate → go-knx server | discovery, connect, write, read, 12 DPT vectors (description: known difference) |
| knxd → go-knx server | connect, write, read, 12 DPT vectors |
| go-knx routing ↔ xknx, KNXUltimate, Calimero tools, knxd | both directions |
| probe → go-knx server | all 24 negative checks |
| Calimero tools, xknx, KNXUltimate → go-knx server over TCP | write, read |
| go-knx → Calimero server over TCP | write, read (and feature services in go-knx's interop suite) |
| Calimero tools → go-knx server: device management, busmonitor | serial number read; busmonitor sees another client's write |
| go-knx → Calimero server: device management | serial number read |
| go-knx, Calimero tools busmonitor → knxd server | see a write of another client |
| xknx, Calimero tools → go-knx secure server | secure session with bound user address, write, read; Data Secure through the tunnel (xknx); device management as user 1 (Calimero tools); plain connections refused |
| go-knx → Calimero secure server | secure session, write, read, Data Secure through the tunnel (decrypted by xknx), device management as user 1 |
| go-knx secure routing ↔ xknx, Calimero tools | both directions, with Data Secure (Calimero tools → go-knx through go-knx as the surrogate) |
| Secure sessions over UDP | go-knx and Calimero tools → go-knx and Calimero servers: connect, write, read |
| Servers' secure routing (go-knx, Calimero) | in from xknx, Calimero tools and go-knx routers; out to them from a secure tunnel |
| Third-party pairs (for example xknx → knxd, Calimero → knxd) | as reported; they validate the harness and the peers |

Multiple clients: every server is used by the client, the observer and,
for reads, the responder at the same time (three concurrent tunnels); the
probe opens connections until the server refuses (go-knx and knxd: eight,
then E_NO_MORE_CONNECTIONS).

## Known differences

| Implementation | Difference | Evidence |
|---|---|---|
| KNXUltimate 6.3.1 | Its DESCRIPTION_REQUEST announces port 3671 while it listens on an ephemeral port, so servers that answer to the HPAI (all three here) are not heard | src/KNXClient.ts `sendDescriptionRequestMessage`: `new HPAI(localIPAddress)` with the default port |
| calimero-server 3.0-M1 | About 10 s without answers after a 3-octet datagram, and after a CONNECT_REQUEST whose CRI has length 0; its log shows the control endpoint starting again | probe negative suite; server log |

## Failures investigated and fixed

Two failures between third-party implementations were analysed and fixed
in the harness (2026-10-29):

| Failure | Root cause | Fix |
|---|---|---|
| knxd client → calimero-server, a DPT write lost every full run | knxd 0.14.73's `ipt` client builds its DISCONNECT_REQUEST on shutdown but closes the socket before sending it, so every short-lived knxd client left a dead tunnel on the server. The dead tunnels filled calimero-server's eight slots, and the adapter reported a write as passed without a tunnel, because knxtool only hands the telegram to the local daemon. | The knxd adapter now waits for the CONNECT_RESPONSE, requires the L_Data.con of each write, and sends the missing DISCONNECT_REQUEST itself. Reported as [knxd#667](https://github.com/knxd/knxd/issues/667). |
| probe → calimero-server, heartbeat on an open channel | The check ran right after calimero-server's control endpoint restart. In that window Calimero answers E_KNX_CONNECTION (0x27): its subnet reports a non-zero MEDIUM_STATUS (`ControlEndpointService.subnetStatus`). The probe also waited only 2 s, where the standard gives the server 10 s. | The connection checks run before the malformed-input checks; the heartbeat waits the standard's 10 s; a heartbeat right after the malformed input is recorded as an observation. |

## Reported upstream

| Project | Report | Status |
|---|---|---|
| KNXUltimate | [#117](https://github.com/Supergiovane/KNXUltimate/issues/117): the description request announces port 3671 | open |
| calimero-tools | [#24](https://github.com/calimero-project/calimero-tools/issues/24): `describe --json --nat` NullPointerException | open |
| knxd | [#667](https://github.com/knxd/knxd/issues/667): the `ipt` client never sends its DISCONNECT_REQUEST | open |
| calimero-server | not reported: the control endpoint crash is fixed on master (d276d8a8), not released yet | — |

## Other observations

- KNX Secure: calimero-server 3.0-M1's secure routing needs a latency
  tolerance (`<routing latencyTolerance="1000">`) and fails in the official
  image with "module io.calimero.core does not open io.calimero.knxnetip
  to module io.calimero.server" unless the JVM runs with `--add-opens
  io.calimero.core/io.calimero.knxnetip=io.calimero.server`; the adapter
  sets both.
- KNX Secure: Calimero tools send Data Secure group telegrams through a
  surrogate device (S-A_Sync, then A_FunctionPropertyExt_Command for group
  object diagnostics, object type 9, PID 66, with the surrogate's tool
  key); every sender of the group in the keyring must be a device with a
  tool key. go-knx acts as the surrogate.
- KNX Secure: Calimero server 3.0-M1 ends a secure session when its tunnel
  disconnects, and logs the client's following SESSION_STATUS close as
  "invalid session ID"; xknx and go-knx both send it, harmlessly.
- KNX Secure: a client killed without disconnecting keeps a secure user's
  bound address on Calimero server until the connection times out; the
  matrix therefore lets responders end by themselves, and the Calimero
  tools adapter connects with a read instead of a killed `groupmon`.
- KNX Secure: Calimero server and go-knx both refuse plain connections to a
  secure server with E_CONNECTION_TYPE, and allow secure device
  management for the management user (1) only.
- Calimero tools open a device management connection after a tunnel; the
  go-knx server refuses it (E_CONNECTION_TYPE), harmlessly.
- The knxd server drops a source address it learned on an earlier
  tunnelling connection (loop protection); the knxd adapter therefore uses
  knxd's `single` filter as a client.
- go-knx's routing sent telegrams with source 0.0.0 when none was set;
  knxd dropped them. Fixed in go-knx (default 15.15.255), found by this
  matrix.
- go-knx's server announced its own address as the data endpoint to NAT
  clients; fixed (route back endpoint), found by go-knx's interop suite.

## Reproduce

```bash
make images matrix
python3 scripts/matrix-table.py reports/latest.json
```
