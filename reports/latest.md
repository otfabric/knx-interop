# knx-interop results

Started 2026-10-30T02:39:29.949924+00:00, finished 2026-10-30T02:47:46.871324+00:00 on darwin/arm64.

Summary: known-difference 5, pass 215, unsupported 39

## Implementations

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| calimero-server | calimero-server | 3.0-M1 | server |
| calimero-tools | calimero | 3.0-M1 | client |
| knxd | knxd | 0.14.73 | server, client |
| knxultimate | knxultimate | 6.3.1 | client |
| probe | probe | 1.0 | client |
| xknx | xknx | 4.0.0 | client |

## tunnel

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| discover (multicast search) | xknx | knxd | PASS |  |
| describe | xknx | knxd | PASS |  |
| connect and disconnect | xknx | knxd | PASS |  |
| group write (DPT 1.001) | xknx | knxd | PASS | observer/responder calimero-tools.  |
| group read/response (DPT 9.001) | xknx | knxd | PASS | observer/responder knxultimate.  |
| discover (multicast search) | knxultimate | knxd | PASS |  |
| describe | knxultimate | knxd | KNOWN-DIFFERENCE | KNXUltimate 6.3.1 announces <local IP>:3671 in its DESCRIPTION_REQUEST HPAI while it listens on an ephemeral port (src/KNXClient.ts sendDescriptionRequestMessage: new HPAI(localIPAddress), default port 3671); servers that answer to the HPAI, as the standard requires, answer a port nobody listens on. |
| connect and disconnect | knxultimate | knxd | PASS |  |
| group write (DPT 1.001) | knxultimate | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxultimate | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | knxd | PASS |  |
| describe | calimero-tools | knxd | PASS |  |
| connect and disconnect | calimero-tools | knxd | PASS |  |
| group write (DPT 1.001) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | knxd | PASS |  |
| group write (DPT 1.001) | knxd | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxd | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | xknx | calimero-server | PASS |  |
| describe | xknx | calimero-server | PASS |  |
| connect and disconnect | xknx | calimero-server | PASS |  |
| group write (DPT 1.001) | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| group read/response (DPT 9.001) | xknx | calimero-server | PASS | observer/responder knxultimate.  |
| discover (multicast search) | knxultimate | calimero-server | PASS |  |
| describe | knxultimate | calimero-server | PASS |  |
| connect and disconnect | knxultimate | calimero-server | PASS |  |
| group write (DPT 1.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | calimero-server | PASS |  |
| describe | calimero-tools | calimero-server | PASS |  |
| connect and disconnect | calimero-tools | calimero-server | PASS |  |
| group write (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | calimero-server | PASS |  |
| group write (DPT 1.001) | knxd | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxd | calimero-server | PASS | observer/responder xknx.  |

## dpt

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| DPT 1.001 on | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 1.001 off | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 5.001 100 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 5.010 200 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 7.001 4660 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 9.001 21.5 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 9.001 -30 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 9.004 1200 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 12.001 305419896 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 13.001 -2 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 14.056 1234.5 | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 16.000 KNX interop | xknx | knxd | PASS | observer/responder calimero-tools.  |
| DPT 1.001 on | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 off | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 5.001 100 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 5.010 200 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | knxultimate | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 on | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 off | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 5.001 100 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 5.010 200 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | calimero-tools | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 on | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 off | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 5.001 100 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 5.010 200 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | knxd | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 on | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 1.001 off | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 5.001 100 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 5.010 200 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 7.001 4660 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 9.001 21.5 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 9.001 -30 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 9.004 1200 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 12.001 305419896 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 13.001 -2 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 14.056 1234.5 | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 16.000 KNX interop | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| DPT 1.001 on | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 off | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.001 100 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.010 200 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 on | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 off | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.001 100 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.010 200 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 on | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 off | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.001 100 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.010 200 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | knxd | calimero-server | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | knxd | calimero-server | PASS | observer/responder xknx.  |

## v2

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| group write over TCP (DPT 1.001) | xknx | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | xknx | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | xknx | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | xknx | knxd | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxultimate | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | knxultimate | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | knxultimate | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxultimate | knxd | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | calimero-tools | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | calimero-tools | knxd | UNSUPPORTED | no device management on the server |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| group write over TCP (DPT 1.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | knxd | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| group read over TCP (DPT 9.001) | xknx | calimero-server | PASS | observer/responder knxultimate.  |
| device management: device serial number (M_PropRead) | xknx | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | xknx | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | knxultimate | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxultimate | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | calimero-tools | calimero-server | PASS |  |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | calimero-server | UNSUPPORTED | no busmonitor on the server |
| group write over TCP (DPT 1.001) | knxd | calimero-server | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | calimero-server | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | calimero-server | UNSUPPORTED | no busmonitor on the client |

## negative

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| heartbeat on an open channel → E_NO_ERROR | probe | knxd | PASS | status 0x00 after 0.0 s |
| TUNNELLING_REQUEST sequence 0 acknowledged | probe | knxd | PASS | ack status 0 |
| repeated sequence 0 acknowledged again (duplicate) | probe | knxd | PASS | ack status 0 |
| out-of-order sequence 5 not acknowledged | probe | knxd | PASS | ack status None |
| sequence numbers roll over 255 → 0 | probe | knxd | PASS | 259 requests acknowledged |
| DISCONNECT_REQUEST → E_NO_ERROR | probe | knxd | PASS | DISCONNECT_RESPONSE |
| heartbeat after disconnect → E_CONNECTION_ID | probe | knxd | PASS | status 0x21 |
| survives header length 7 | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives protocol version 0x20 | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length longer than the datagram | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length shorter than the datagram | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives truncated header | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives unknown service type 0x0F00 | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives HPAI of length 7 | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives 2000-octet datagram | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives empty CONNECT_REQUEST | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives CRI length 0 | probe | knxd | PASS | answers DESCRIPTION_REQUEST afterwards |
| CONNECTIONSTATE_REQUEST of an unknown channel → E_CONNECTION_ID | probe | knxd | PASS | status 0x21 |
| unsupported connection type → E_CONNECTION_TYPE | probe | knxd | PASS | status 0x22 |
| raw tunnelling layer → refused | probe | knxd | PASS | observed: status 0x29 |
| TCP HPAI over UDP → refused | probe | knxd | PASS | observed: status None |
| heartbeat right after the malformed datagrams | probe | knxd | PASS | observed: status 0x00 after 0.0 s |
| channel exhaustion → E_NO_MORE_CONNECTIONS | probe | knxd | PASS | 7 connections, then status 0x24 |
| still serving after the tests | probe | knxd | PASS | answers DESCRIPTION_REQUEST |
| heartbeat on an open channel → E_NO_ERROR | probe | calimero-server | PASS | status 0x00 after 0.0 s |
| TUNNELLING_REQUEST sequence 0 acknowledged | probe | calimero-server | PASS | ack status 0 |
| repeated sequence 0 acknowledged again (duplicate) | probe | calimero-server | PASS | ack status 0 |
| out-of-order sequence 5 not acknowledged | probe | calimero-server | PASS | ack status None |
| sequence numbers roll over 255 → 0 | probe | calimero-server | PASS | 259 requests acknowledged |
| DISCONNECT_REQUEST → E_NO_ERROR | probe | calimero-server | PASS | DISCONNECT_RESPONSE |
| heartbeat after disconnect → E_CONNECTION_ID | probe | calimero-server | PASS | status 0x21 |
| survives header length 7 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives protocol version 0x20 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length longer than the datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length shorter than the datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives truncated header | probe | calimero-server | KNOWN-DIFFERENCE | calimero-server 3.0-M1 stops answering for about 10 s after a 3-octet datagram: its log shows the control endpoint coming up again ("control endpoint ... is up and running"); cause: an uncaught KNXIllegalArgumentException ("negative length of message body") in UdpServiceLooper closes the control end |
| survives unknown service type 0x0F00 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives HPAI of length 7 | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives 2000-octet datagram | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives empty CONNECT_REQUEST | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives CRI length 0 | probe | calimero-server | KNOWN-DIFFERENCE | calimero-server 3.0-M1 stops answering for about 10 s after a CONNECT_REQUEST whose CRI has length 0, the same uncaught exception as after a truncated header; fixed upstream by d276d8a8 (observed: no DESCRIPTION_RESPONSE for 10 s, then the server answered again) |
| CONNECTIONSTATE_REQUEST of an unknown channel → E_CONNECTION_ID | probe | calimero-server | PASS | status 0x21 |
| unsupported connection type → E_CONNECTION_TYPE | probe | calimero-server | PASS | status 0x22 |
| raw tunnelling layer → refused | probe | calimero-server | PASS | observed: status 0x29 |
| TCP HPAI over UDP → refused | probe | calimero-server | PASS | observed: status 0x00 |
| heartbeat right after the malformed datagrams | probe | calimero-server | PASS | observed: status 0x00 after 0.0 s |
| channel exhaustion → E_NO_MORE_CONNECTIONS | probe | calimero-server | PASS | 8 connections, then status 0x24 |
| still serving after the tests | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST |

## routing

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| routing write (multicast) | xknx | knxultimate | PASS |  |
| routing write (multicast) | xknx | calimero-tools | PASS |  |
| routing write (multicast) | xknx | knxd | PASS |  |
| routing write (multicast) | knxultimate | xknx | PASS |  |
| routing write (multicast) | knxultimate | calimero-tools | PASS |  |
| routing write (multicast) | knxultimate | knxd | PASS |  |
| routing write (multicast) | calimero-tools | xknx | PASS |  |
| routing write (multicast) | calimero-tools | knxultimate | PASS |  |
| routing write (multicast) | calimero-tools | knxd | PASS |  |
| routing write (multicast) | knxd | xknx | PASS |  |
| routing write (multicast) | knxd | knxultimate | PASS |  |
| routing write (multicast) | knxd | calimero-tools | PASS |  |

## secure

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| secure tunnelling server | - | knxd | UNSUPPORTED | no KNX IP Secure server |
| secure session over UDP (user 2) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group write over UDP (DPT 1.001) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group read/response over UDP (DPT 9.001) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure device management: serial number (user 1) | xknx | calimero-server | UNSUPPORTED | no device management on the client |
| secure tunnelling | knxultimate | calimero-server | UNSUPPORTED | no KNX IP Secure client |
| secure tunnelling | knxd | calimero-server | UNSUPPORTED | no KNX IP Secure client |
| secure session connect (user 2, bound address) | xknx | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| secure tunnel group read/response (DPT 9.001) | xknx | calimero-server | UNSUPPORTED | no responder for this client among the adapters |
| Data Secure group write through a secure tunnel (DPT 9.001) | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| secure session connect (user 2, bound address) | calimero-tools | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure tunnel group read/response (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | calimero-tools | calimero-server | KNOWN-DIFFERENCE | observer/responder xknx. calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device (S-A_Sync and group object diagnostics with the surrogate's tool key) and require every sender of the group in the keyring to be such a device; the profile's tunnel groups list the tunnel  |
| secure session over UDP (user 2) | calimero-tools | calimero-server | PASS |  |
| secure group write over UDP (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure group read/response over UDP (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure device management: serial number (user 1) | calimero-tools | calimero-server | PASS |  |
| plain connection refused by the secure server | xknx | calimero-server | PASS |  |
| secure routing | knxultimate | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing | knxd | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing write (DPT 1.001) | xknx | calimero-tools | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | xknx | calimero-tools | PASS |  |
| secure routing write (DPT 1.001) | calimero-tools | xknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | xknx | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device; xknx does not act as one, and the pairing has no go-knx on the network. Towards go-knx, the surrogate, it passes. (observed: 02:46:49.892 [ERROR  ] io.calimero.tools.ProcComm: completed with error io.calimero.sec |
| server secure routing | - | knxd | UNSUPPORTED | no secure routing in the server |
| secure routing into the server, seen by a secure tunnel | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| secure routing into the server, seen by a secure tunnel | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
