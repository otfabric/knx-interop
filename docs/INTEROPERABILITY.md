# Interoperability matrix

Run of 2026-10-29 on Docker Desktop (macOS, arm64), report
[reports/latest.json](../reports/latest.json) /
[reports/latest.md](../reports/latest.md): **331 pass, 5 known
differences, 6 unsupported, 2 fail** (344 results). Each cell counts the
results in which that implementation took the role named in the row (every
pairing with every other implementation; go-knx is in most cells as a peer
or an observer).

Versions: calimero-server and calimero-tools 3.0-M1 (official images,
pinned by digest), knxd 0.14.73-1 (Debian trixie), xknx 4.0.0, KNXUltimate
6.3.1, go-knx from source (feat/foundation, knxctl feat/cli), probe 1.0.

| Feature | calimero | knxd | xknx | KNXUltimate | go-knx |
|---|---|---|---|---|---|
| Discovery (as client) | PASS (3) | UNSUPPORTED 3 | PASS (3) | PASS (3) | PASS (3) |
| Description (as client) | PASS (3) | UNSUPPORTED 3 | PASS (3) | KNOWN DIFFERENCE 3 | PASS (3) |
| Tunnelling client | PASS (3) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| Tunnelling server | PASS (10) | PASS (10) | UNSUPPORTED (no server) | UNSUPPORTED (adapter: client only) | PASS (10) |
| Group write | PASS (3) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| Group read (client) | PASS (3) | PASS (3) | PASS (3) | PASS (3) | PASS (3) |
| Group response (responder/observer) | NOT TESTED | NOT TESTED | PASS (12) | NOT TESTED | PASS (3) |
| Routing (sender) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| Routing (receiver) | PASS (4) | PASS (4) | PASS (4) | PASS (4) | PASS (4) |
| DPT encoding (sender) | PASS (36) | FAIL 1, PASS 35 | PASS (36) | PASS (36) | PASS (36) |
| DPT decoding (observer) | NOT TESTED | NOT TESTED | PASS (36) | NOT TESTED | FAIL 1, PASS 143 |
| Negative tests (server) | FAIL 1, KNOWN DIFFERENCE 2, PASS 20 | PASS (23) | NOT TESTED | NOT TESTED | PASS (23) |
| IP Secure | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Data Secure | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

Legend: PASS, FAIL, UNSUPPORTED (the stack or its adapter does not offer
it), NOT TESTED (no scenario uses the implementation in that role yet),
KNOWN DIFFERENCE (a verified deviation, below). HARDWARE REQUIRED and
BLOCKED do not occur in this run: nothing needs hardware, and the secure
rows are not tested because go-knx does not implement KNX Secure yet.

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
| probe → go-knx server | all 23 negative checks |
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

## Open failures (third-party pairs)

Both are listed in tests/known-differences.tsv as UNEXPLAINED, so they
appear as known-difference in later reports and do not gate CI; they are
not understood yet.

| Result | Notes |
|---|---|
| knxd client → calimero-server, DPT 5.010 200 | The go-knx observer receives no telegram; reproducible in every full run, locally and in CI; it passes in isolation with xknx and with go-knx observing; the same write through knxd's and go-knx's servers passes, and DPT 5.010 from every other client to Calimero passes. Not analysed further yet |
| probe → calimero-server, heartbeat on an open channel | Intermittent (passed in an earlier run); the check runs shortly after Calimero recovered from the CRI-length-0 outage |

## Other observations

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
