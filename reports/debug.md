# knx-interop results

Started 2026-10-29T17:51:03.257113+00:00, finished 2026-10-29T17:51:27.515284+00:00 on darwin/arm64.

Summary: fail 2, pass 21

## Implementations

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| calimero-server | calimero-server | 3.0-M1 | server |
| goknx | go-knx | v0.0.0 (knxctl dev) | server, client |

## negative

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| survives header length 7 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives protocol version 0x20 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length longer than the datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length shorter than the datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives truncated header | probe | calimero-server | FAIL | no DESCRIPTION_RESPONSE for 10 s, then the server answered again |
| survives unknown service type 0x0F00 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives HPAI of length 7 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives 2000-octet datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives empty CONNECT_REQUEST | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives CRI length 0 | probe | calimero-server | FAIL | no DESCRIPTION_RESPONSE for 10 s, then the server answered again |
| CONNECTIONSTATE_REQUEST of an unknown channel → E_CONNECTION_ID | probe | calimero-server | PASS | status 0x21 |
| unsupported connection type → E_CONNECTION_TYPE | probe | calimero-server | PASS | status 0x22 |
| raw tunnelling layer → refused | probe | calimero-server | PASS | status 0x29 |
| TCP HPAI over UDP → refused | probe | calimero-server | PASS | status 0x00 |
| heartbeat on an open channel → E_NO_ERROR | probe | calimero-server | PASS | CONNECTIONSTATE_RESPONSE |
| TUNNELLING_REQUEST sequence 0 acknowledged | probe | calimero-server | PASS | ack status 0 |
| repeated sequence 0 acknowledged again (duplicate) | probe | calimero-server | PASS | ack status 0 |
| out-of-order sequence 5 not acknowledged | probe | calimero-server | PASS | ack status None |
| sequence numbers roll over 255 → 0 | probe | calimero-server | PASS | 259 requests acknowledged |
| DISCONNECT_REQUEST → E_NO_ERROR | probe | calimero-server | PASS | DISCONNECT_RESPONSE |
| heartbeat after disconnect → E_CONNECTION_ID | probe | calimero-server | PASS | status 0x21 |
| channel exhaustion → E_NO_MORE_CONNECTIONS | probe | calimero-server | PASS | 8 connections, then status 0x24 |
| still serving after the tests | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST |
