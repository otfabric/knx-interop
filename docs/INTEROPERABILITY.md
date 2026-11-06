# Interoperability matrix

Run of 2026-11-06 on Docker Desktop (macOS, arm64), report
[reports/latest.json](../reports/latest.json) /
[reports/latest.md](../reports/latest.md): **319 pass, 12 known
differences, 85 unsupported, 0 fail** (416 results), the third-party stacks
among themselves. Each cell counts the results in which that
implementation took the role named in the row.

Versions: calimero-server and calimero-tools 3.0-M1 (official images,
pinned by digest), knxd 0.14.73-1 (Debian trixie), xknx 4.1.1, KNXUltimate
6.3.2, cB-Sigma knx v0.2.0 and knx-sim v0.2.0, probe 1.0.

A system under test runs this matrix from its own repository with its own
adapter (`--adapter`): go-knx's results are in
[go-knx's INTEROPERABILITY.md](https://github.com/otfabric/go-knx/blob/main/INTEROPERABILITY.md)
(`make -C ../go-knx interop-matrix` from a go-knx checkout next to this one).

| Feature | calimero | knxd | xknx | KNXUltimate | cB-Sigma |
|---|---|---|---|---|---|
| Discovery (as client) | PASS (2) | UNSUPPORTED 2 | PASS (2) | PASS (2) | PASS (2) |
| Description (as client) | PASS (2) | UNSUPPORTED 2 | PASS (2) | PASS (2) | PASS (2) |
| Tunnelling client | PASS (2) | PASS (2) | PASS (2) | PASS (2) | PASS (2) |
| Tunnelling server | PASS (10) | PASS (10) | NOT TESTED | NOT TESTED | NOT TESTED |
| Group write | PASS 3, UNSUPPORTED 1 | PASS 2, UNSUPPORTED 2 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 |
| Group read (client) | PASS 3, UNSUPPORTED 1 | PASS 2, UNSUPPORTED 2 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 | PASS 3, UNSUPPORTED 1 |
| Group response (responder/observer) | NOT TESTED | NOT TESTED | PASS (11) | PASS (3) | NOT TESTED |
| Routing (sender) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| Routing (receiver) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| DPT encoding (sender) | PASS (24) | PASS (24) | PASS (24) | PASS (24) | PASS (24) |
| DPT decoding (observer) | PASS (24) | NOT TESTED | PASS (96) | NOT TESTED | NOT TESTED |
| Negative tests (server) | KNOWN DIFFERENCE 2, PASS 22 | PASS (24) | NOT TESTED | NOT TESTED | NOT TESTED |
| Tunnelling over TCP (client) | PASS 2, UNSUPPORTED 2 | UNSUPPORTED 4 | PASS 2, UNSUPPORTED 2 | PASS 2, UNSUPPORTED 2 | PASS 2, UNSUPPORTED 2 |
| Tunnelling over TCP (server) | PASS 8, UNSUPPORTED 2 | UNSUPPORTED 10 | NOT TESTED | NOT TESTED | NOT TESTED |
| Device management (client) | PASS 1, UNSUPPORTED 1 | UNSUPPORTED 2 | UNSUPPORTED 2 | UNSUPPORTED 2 | UNSUPPORTED 2 |
| Device management (server) | PASS 1, UNSUPPORTED 4 | UNSUPPORTED 5 | NOT TESTED | NOT TESTED | NOT TESTED |
| Busmonitor (client) | PASS 1, UNSUPPORTED 1 | UNSUPPORTED 2 | UNSUPPORTED 2 | UNSUPPORTED 2 | PASS 1, UNSUPPORTED 1 |
| Busmonitor (server) | UNSUPPORTED 5 | PASS 2, UNSUPPORTED 3 | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure tunnelling (client) | PASS (3) | UNSUPPORTED 1 | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 1 | PASS (3) |
| IP Secure tunnelling (server) | PASS 9, UNSUPPORTED 3 | UNSUPPORTED 1 | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure sessions over UDP (client) | PASS (3) | NOT TESTED | UNSUPPORTED 3 | NOT TESTED | UNSUPPORTED 3 |
| IP Secure sessions over UDP (server) | PASS 3, UNSUPPORTED 6 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure device management (client) | PASS (1) | NOT TESTED | UNSUPPORTED 1 | NOT TESTED | UNSUPPORTED 1 |
| IP Secure device management (server) | PASS 1, UNSUPPORTED 2 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| IP Secure routing (sender) | PASS (2) | UNSUPPORTED 1 | PASS (2) | UNSUPPORTED 1 | PASS (2) |
| IP Secure routing (receiver) | PASS (2) | NOT TESTED | PASS (2) | NOT TESTED | PASS (2) |
| IP Secure routing (server) | PASS (6) | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Data Secure (sender) | KNOWN DIFFERENCE 3 | NOT TESTED | PASS (3) | NOT TESTED | PASS (3) |
| Data Secure (receiver) | PASS (3) | NOT TESTED | KNOWN DIFFERENCE 2, PASS 2 | NOT TESTED | KNOWN DIFFERENCE 1, PASS 1 |
| Remote property services (tool) | PASS (3) | UNSUPPORTED 1 | PASS 2, UNSUPPORTED 1 | UNSUPPORTED 1 | UNSUPPORTED 1 |
| Remote property services (device) | PASS 5, UNSUPPORTED 4 | UNSUPPORTED 1 | NOT TESTED | NOT TESTED | NOT TESTED |
| Data Secure tool access (tool) | UNSUPPORTED 3 | NOT TESTED | UNSUPPORTED 3 | NOT TESTED | NOT TESTED |
| Data Secure tool access (device) | UNSUPPORTED 8 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| knx-sim: tunnelling, repeats, missing acks (client) | PASS (6) | PASS 4, UNSUPPORTED 2 | KNOWN DIFFERENCE 1, PASS 5 | KNOWN DIFFERENCE 1, PASS 5 | NOT TESTED |
| knx-sim: IP Secure and Data Secure (client) | KNOWN DIFFERENCE 2, PASS 2 | UNSUPPORTED 4 | PASS (4) | UNSUPPORTED 4 | NOT TESTED |
| knx-sim: secure session faults (client) | KNOWN DIFFERENCE 1, PASS 3 | UNSUPPORTED 4 | PASS (4) | UNSUPPORTED 4 | NOT TESTED |
| knx-sim router: flow control (client) | UNSUPPORTED 2 | KNOWN DIFFERENCE 1, PASS 1 | PASS (2) | KNOWN DIFFERENCE 1, PASS 1 | NOT TESTED |
| ETS keyring import (offline) | UNSUPPORTED 1 | UNSUPPORTED 1 | UNSUPPORTED 1 | UNSUPPORTED 1 | PASS (3) |

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
cB-Sigma knx is a client in all of these. The sim suite runs every other
client against cB-Sigma knx-sim: a fresh simulated gateway or router per
scenario, driven through `sim-ctl` (faults injected, what it received read
back); the files suite has each adapter with the `keyring` operation read
two ETS keyrings offline, and its results are kept apart from the wire
protocol rows above.
Remote device management (contract 1.4): Calimero tools and xknx manage
Calimero server's device; the tool access scenarios need a device with a
tool key, which none of the third-party servers offers, so they run only
with a system under test as the device (go-knx).

## Known differences

| Implementation | Difference | Evidence |
|---|---|---|
| calimero-server 3.0-M1 | About 10 s without answers after a 3-octet datagram, and after a CONNECT_REQUEST whose CRI has length 0; its log shows the control endpoint starting again | probe negative suite; server log |
| knxd 0.14.73 | Ignores ROUTING_BUSY: answered 31 to 114 ms after a ROUTING_BUSY with wait time 500 ms | sim suite; its router backend has no handling for it |
| KNXUltimate 6.3.2 | Ignores ROUTING_BUSY (an error event only; answered after 5 ms); `write` is fire and forget, so an unacknowledged tunnelling request is not reported | sim suite; `KNXClient.ts` |
| xknx 4.1.1 | Repeats an unacknowledged TUNNELLING_REQUEST once and closes the tunnel, as the standard asks, but its telegram queue only logs the failure: the application's write does not fail | sim suite; `telegram_queue.py` |
| calimero-tools 3.0-M1 | Keeps its tunnel and connection after the gateway's SESSION_STATUS close (still open 18 s later) | sim suite |

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
| KNXUltimate | [#117](https://github.com/Supergiovane/KNXUltimate/issues/117): the description request announces port 3671 | fixed in 6.3.2 |
| calimero-tools | [#24](https://github.com/calimero-project/calimero-tools/issues/24): `describe --json --nat` NullPointerException | open |
| knxd | [#667](https://github.com/knxd/knxd/issues/667): the `ipt` client never sends its DISCONNECT_REQUEST | open |
| calimero-server | not reported: the control endpoint crash is fixed on master (d276d8a8), not released yet | — |
| knxd | [#669](https://github.com/knxd/knxd/issues/669): ROUTING_BUSY is not acted on | open, tracked in [#21](https://github.com/otfabric/knx-interop/issues/21) |
| KNXUltimate | [#118](https://github.com/Supergiovane/KNXUltimate/issues/118): ROUTING_BUSY only emits an error | open, tracked in [#22](https://github.com/otfabric/knx-interop/issues/22) |
| KNXUltimate | [#119](https://github.com/Supergiovane/KNXUltimate/issues/119): `write()` cannot report an unacknowledged request (feature request) | open, tracked in [#23](https://github.com/otfabric/knx-interop/issues/23) |
| xknx | [#2024](https://github.com/XKNX/xknx/issues/2024): queued telegrams cannot report a send failure (feature request) | open, tracked in [#24](https://github.com/otfabric/knx-interop/issues/24) |
| calimero-core | [#181](https://github.com/calimero-project/calimero-core/issues/181): SESSION_STATUS close ignored after authentication | open, tracked in [#25](https://github.com/otfabric/knx-interop/issues/25) |
| cB-Sigma knx-sim | [#1](https://github.com/cB-Sigma/knx-sim/issues/1): tunnel addresses grow beyond the announced slots | open, tracked in [#26](https://github.com/otfabric/knx-interop/issues/26) |
| cB-Sigma knx | [#1](https://github.com/cB-Sigma/knx/issues/1): the plain router pauses on its own ROUTING_BUSY | open, tracked in [#27](https://github.com/otfabric/knx-interop/issues/27) |
| calimero-core | [#176](https://github.com/calimero-project/calimero-core/issues/176) (by another reporter): S-A_Sync_Res random loses trailing zero octets | fixed on master (368d0929), not released yet |

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
- Remote device management: Calimero 3.0-M1 rebuilds the random of an
  S-A_Sync_Res with `BitSet.toByteArray()`, which drops trailing zero
  octets; a random ending in 0x00 (about 1 sync in 256) then fails with
  "MAC mismatch" and the tool access scenario fails once. Seen with Calimero
  tools against the go-knx server in a local full matrix; the captured
  frames are valid AES-CCM. Not a waiver (a waiver that passes fails the
  run); a rerun passes. calimero-core#176, fixed on master, not released.
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

## cB-Sigma knx and knx-sim

Found while adding them (2026-11-06), each in a real run; reported as
[knx-sim#1](https://github.com/cB-Sigma/knx-sim/issues/1) and
[knx#1](https://github.com/cB-Sigma/knx/issues/1) (tracked in [#26](https://github.com/otfabric/knx-interop/issues/26), #27):

- knx-sim v0.2.0 gives a tunnel the address 1.1.(240 + channel) and never
  reuses a channel number, so from the fifth connection of a simulator's
  life its tunnels get 1.1.245 and up: outside the four slots its extended
  search announces (1.1.241 to 1.1.244) and the Data Secure senders it
  documents. cB-Sigma knx's Data Secure write from 1.1.245 was refused
  (`dataSecureRefused` 2); on a fresh simulator the same write and read
  pass. Channel 15 would get 1.1.255, the gateway's own address. The sim
  suite starts a fresh simulator for every scenario.
- cB-Sigma knx v0.2.0's router counts its own ROUTING_BUSY, seen on the
  multicast loopback, and then sometimes holds back its own next frame
  for the wait time (one run of two). knx-sim's test reads therefore leave
  through a socket of their own.
- knx-sim keeps a tunnel's group writes to itself (other tunnels do not
  see them) and has a fixed friendly name, so it is no contract server.
- Calimero tools 3.0-M1's monitor starts listening about 3 s after it
  reports the connection (it first tries a device management connection,
  which knx-sim refuses); the sim suite waits 4 s.

OT Fabric's own go-knx v0.8.0 against knx-sim and cB-Sigma knx (local run
with `scripts/interop.sh otfabric xknx knxultimate cbsigma probe`: 202 pass,
3 known differences of xknx and KNXUltimate, 0 fail): it honours ROUTING_BUSY
(answer 513 ms after a ROUTING_BUSY with wait time 500 ms), keeps answering
after ROUTING_LOST_MESSAGE, discards replayed and tampered secure wrappers,
drops a session the gateway closes, keeps an idle secure session past the
60 s timeout with keepalives, delivers a repeated indication once, reports
an unacknowledged request as a failure and reads both keyrings. cB-Sigma knx
as a client of the go-knx server passes the tunnel, TCP, busmonitor, secure
and routing scenarios.

## Reproduce

```bash
make images matrix
python3 scripts/matrix-table.py reports/latest.json
```
