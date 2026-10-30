# Interoperability matrix

Run of 2026-10-30 on Docker Desktop (macOS, arm64), report
[reports/latest.json](../reports/latest.json) /
[reports/latest.md](../reports/latest.md): **220 pass, 5 known
differences, 51 unsupported, 0 fail** (276 results), the third-party stacks
among themselves. Each cell counts the results in which that
implementation took the role named in the row.

Versions: calimero-server and calimero-tools 3.0-M1 (official images,
pinned by digest), knxd 0.14.73-1 (Debian trixie), xknx 4.0.0, KNXUltimate
6.3.1, probe 1.0.

A system under test runs this matrix from its own repository with its own
adapter (`--adapter`): go-knx's results are in
[go-knx's INTEROPERABILITY.md](https://github.com/otfabric/go-knx/blob/main/INTEROPERABILITY.md)
(`make -C ../go-knx interop-matrix` from a go-knx checkout next to this one).

| Feature | calimero | knxd | xknx | KNXUltimate |
|---|---|---|---|---|
| Discovery (as client) | PASS (2) | UNSUPPORTED 2 | PASS (2) | PASS (2) |
| Description (as client) | PASS (2) | UNSUPPORTED 2 | PASS (2) | KNOWN DIFFERENCE 1, PASS 1 |
| Tunnelling client | PASS (2) | PASS (2) | PASS (2) | PASS (2) |
| Tunnelling server | PASS (8) | PASS (8) | NOT TESTED | NOT TESTED |
| Group write | PASS 3, UNSUPPORTED 1 | PASS 2, UNSUPPORTED 2 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 |
| Group read (client) | PASS 3, UNSUPPORTED 1 | PASS 2, UNSUPPORTED 2 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 |
| Group response (responder/observer) | NOT TESTED | NOT TESTED | PASS (8) | PASS (3) |
| Routing (sender) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| Routing (receiver) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| DPT encoding (sender) | PASS (24) | PASS (24) | PASS (24) | PASS (24) |
| DPT decoding (observer) | PASS (24) | NOT TESTED | PASS (72) | NOT TESTED |
| Negative tests (server) | KNOWN DIFFERENCE 2, PASS 22 | PASS (24) | NOT TESTED | NOT TESTED |
| Tunnelling over TCP (client) | PASS 2, UNSUPPORTED 2 | UNSUPPORTED 4 | PASS 2, UNSUPPORTED 2 | PASS 2, UNSUPPORTED 2 |
| Tunnelling over TCP (server) | PASS 6, UNSUPPORTED 2 | UNSUPPORTED 8 | NOT TESTED | NOT TESTED |
| Device management (client) | PASS 1, UNSUPPORTED 1 | UNSUPPORTED 2 | UNSUPPORTED 2 | UNSUPPORTED 2 |
| Device management (server) | PASS 1, UNSUPPORTED 3 | UNSUPPORTED 4 | NOT TESTED | NOT TESTED |
| Busmonitor (client) | PASS 1, UNSUPPORTED 1 | UNSUPPORTED 2 | UNSUPPORTED 2 | UNSUPPORTED 2 |
| Busmonitor (server) | UNSUPPORTED 4 | PASS 1, UNSUPPORTED 3 | NOT TESTED | NOT TESTED |
| IP Secure tunnelling (client) | PASS (3) | UNSUPPORTED 1 | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 1 |
| IP Secure tunnelling (server) | PASS 6, UNSUPPORTED 3 | UNSUPPORTED 1 | NOT TESTED | NOT TESTED |
| IP Secure sessions over UDP (client) | PASS (3) | NOT TESTED | UNSUPPORTED 3 | NOT TESTED |
| IP Secure sessions over UDP (server) | PASS 3, UNSUPPORTED 3 | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure device management (client) | PASS (1) | NOT TESTED | UNSUPPORTED 1 | NOT TESTED |
| IP Secure device management (server) | PASS 1, UNSUPPORTED 1 | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure routing (sender) | PASS (1) | UNSUPPORTED 1 | PASS (1) | UNSUPPORTED 1 |
| IP Secure routing (receiver) | PASS (1) | NOT TESTED | PASS (1) | NOT TESTED |
| IP Secure routing (server) | PASS (4) | NOT TESTED | NOT TESTED | NOT TESTED |
| Data Secure (sender) | KNOWN DIFFERENCE 2 | NOT TESTED | PASS (2) | NOT TESTED |
| Data Secure (receiver) | PASS (2) | NOT TESTED | KNOWN DIFFERENCE 2 | NOT TESTED |
| Remote property services (tool) | PASS (3) | UNSUPPORTED 1 | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 1 |
| Remote property services (device) | PASS 5, UNSUPPORTED 3 | UNSUPPORTED 1 | NOT TESTED | NOT TESTED |
| Data Secure tool access (tool) | UNSUPPORTED 3 | NOT TESTED | UNSUPPORTED 3 | NOT TESTED |
| Data Secure tool access (device) | UNSUPPORTED 8 | NOT TESTED | NOT TESTED | NOT TESTED |

Legend: PASS, FAIL, UNSUPPORTED (the stack or its adapter does not offer
it), NOT TESTED (no scenario uses the implementation in that role yet),
KNOWN DIFFERENCE (a verified deviation, below). HARDWARE REQUIRED and
BLOCKED do not occur in this run: nothing needs hardware. The secure rows
use the public test profile of contract 1.2; KNXUltimate and knxd take no
part in them.

## Coverage

Every client against every server (a fresh server for each client) and
every routing stack against every other, in both directions where both stacks offer the role: Calimero tools,
xknx, KNXUltimate and knxd as clients of the Calimero and knxd servers;
routing among xknx, KNXUltimate, Calimero tools and knxd; KNX Secure among
xknx, Calimero tools and Calimero server (secure tunnelling over TCP and
UDP, secure routing, Data Secure, the server's secure routing). Each
secure scenario gets a fresh secure server: a peer stopped while connected
(Calimero tools' monitor) leaves its user's session on Calimero server.
Remote device management (contract 1.4): Calimero tools and xknx manage
Calimero server's device; the tool access scenarios need a device with a
tool key, which none of the third-party servers offers, so they run only
with a system under test as the device (go-knx).

## Known differences

| Implementation | Difference | Evidence |
|---|---|---|
| KNXUltimate 6.3.1 | Its DESCRIPTION_REQUEST announces port 3671 while it listens on an ephemeral port, so servers that answer to the HPAI (all three here) are not heard | src/KNXClient.ts `sendDescriptionRequestMessage`: `new HPAI(localIPAddress)` with the default port |
| calimero-server 3.0-M1 | About 10 s without answers after a 3-octet datagram, and after a CONNECT_REQUEST whose CRI has length 0; its log shows the control endpoint starting again | probe negative suite; server log |

## Failures investigated and fixed

Failures between third-party implementations that were analysed and
fixed in the harness (2026-10-29 and 2026-10-30):

| Failure | Root cause | Fix |
|---|---|---|
| KNXUltimate client → calimero-server, every scenario after its first write failed in some full runs (CI and local) | In those runs Calimero server received KNXUltimate's CONNECT_REQUEST and answered it, then nothing more from that container (no data, no DISCONNECT_REQUEST), while KNXUltimate reported its write as sent. Each such tunnel held one of the server's eight slots until its 120 s timeout, so the following scenarios got E_NO_MORE_CONNECTIONS. It never occurred with the client alone; the lost datagrams were not explained. | The tunnel suite now gives every client a fresh server, so a tunnel one client leaves behind no longer fails the others. |
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
- Remote device management: Calimero tools 3.0-M1 computes the Data
  Secure MAC of tool access over the source address it sends, 0.0.0
  unless given its own address (`-k`), while the tunnelling server
  replaces the source by the tunnel address, so a device refuses the
  frames; the adapter passes the tunnel address. Calimero tools reads the
  property description (A_PropertyDescription_Read) before a property
  access; xknx's management takes answers in transport connections only.
- Calimero server 3.0-M1's emulated device answers the remote property
  services (its friendly name is writable) and reports a security object
  with security mode off; it has no tool key access, also with a keyring.
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
