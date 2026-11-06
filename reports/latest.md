# knx-interop results

Started 2026-11-06T20:03:15.168274+00:00, finished 2026-11-06T20:20:06.122865+00:00 on darwin/arm64.

Summary: known-difference 12, pass 319, unsupported 85

## Implementations

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| calimero-server | calimero-server | 3.0-M1 | server |
| calimero-tools | calimero | 3.0-M1 | client |
| cbsigma | cbsigma | v0.2.0 | client |
| knxd | knxd | 0.14.73 | server, client |
| knxultimate | knxultimate | 6.3.2 | client |
| probe | probe | 1.0 | client |
| xknx | xknx | 4.1.1 | client |

## tunnel

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| discover (multicast search) | xknx | knxd | PASS |  |
| describe | xknx | knxd | PASS |  |
| connect and disconnect | xknx | knxd | PASS |  |
| group write (DPT 1.001) | xknx | knxd | PASS | observer/responder calimero-tools.  |
| group read/response (DPT 9.001) | xknx | knxd | PASS | observer/responder knxultimate.  |
| discover (multicast search) | knxultimate | knxd | PASS |  |
| describe | knxultimate | knxd | PASS |  |
| connect and disconnect | knxultimate | knxd | PASS |  |
| group write (DPT 1.001) | knxultimate | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxultimate | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | knxd | PASS |  |
| group write (DPT 1.001) | knxd | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxd | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | knxd | PASS |  |
| describe | calimero-tools | knxd | PASS |  |
| connect and disconnect | calimero-tools | knxd | PASS |  |
| group write (DPT 1.001) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | cbsigma | knxd | PASS |  |
| describe | cbsigma | knxd | PASS |  |
| connect and disconnect | cbsigma | knxd | PASS |  |
| group write (DPT 1.001) | cbsigma | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | cbsigma | knxd | PASS | observer/responder xknx.  |
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
| discover (multicast search) | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | calimero-server | PASS |  |
| group write (DPT 1.001) | knxd | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | knxd | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | calimero-server | PASS |  |
| describe | calimero-tools | calimero-server | PASS |  |
| connect and disconnect | calimero-tools | calimero-server | PASS |  |
| group write (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | cbsigma | calimero-server | PASS |  |
| describe | cbsigma | calimero-server | PASS |  |
| connect and disconnect | cbsigma | calimero-server | PASS |  |
| group write (DPT 1.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |

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
| DPT 1.001 on | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 off | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 5.001 100 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 5.010 200 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | cbsigma | knxd | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | cbsigma | knxd | PASS | observer/responder xknx.  |
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
| DPT 1.001 on | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 off | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.001 100 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.010 200 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | cbsigma | calimero-server | PASS | observer/responder xknx.  |

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
| group write over TCP (DPT 1.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | knxd | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | calimero-tools | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | calimero-tools | knxd | UNSUPPORTED | no device management on the server |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| group write over TCP (DPT 1.001) | cbsigma | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | cbsigma | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | cbsigma | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | cbsigma | knxd | PASS | observer/responder xknx.  |
| group write over TCP (DPT 1.001) | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| group read over TCP (DPT 9.001) | xknx | calimero-server | PASS | observer/responder knxultimate.  |
| device management: device serial number (M_PropRead) | xknx | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | xknx | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | knxultimate | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxultimate | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxd | calimero-server | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | calimero-server | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | calimero-tools | calimero-server | PASS |  |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | calimero-server | UNSUPPORTED | no busmonitor on the server |
| group write over TCP (DPT 1.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | cbsigma | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | cbsigma | calimero-server | UNSUPPORTED | no busmonitor on the server |

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
| routing write (multicast) | xknx | knxd | PASS |  |
| routing write (multicast) | xknx | calimero-tools | PASS |  |
| routing write (multicast) | xknx | cbsigma | PASS |  |
| routing write (multicast) | knxultimate | xknx | PASS |  |
| routing write (multicast) | knxultimate | knxd | PASS |  |
| routing write (multicast) | knxultimate | calimero-tools | PASS |  |
| routing write (multicast) | knxultimate | cbsigma | PASS |  |
| routing write (multicast) | knxd | xknx | PASS |  |
| routing write (multicast) | knxd | knxultimate | PASS |  |
| routing write (multicast) | knxd | calimero-tools | PASS |  |
| routing write (multicast) | knxd | cbsigma | PASS |  |
| routing write (multicast) | calimero-tools | xknx | PASS |  |
| routing write (multicast) | calimero-tools | knxultimate | PASS |  |
| routing write (multicast) | calimero-tools | knxd | PASS |  |
| routing write (multicast) | calimero-tools | cbsigma | PASS |  |
| routing write (multicast) | cbsigma | xknx | PASS |  |
| routing write (multicast) | cbsigma | knxultimate | PASS |  |
| routing write (multicast) | cbsigma | knxd | PASS |  |
| routing write (multicast) | cbsigma | calimero-tools | PASS |  |

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
| secure session over UDP (user 2) | cbsigma | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group write over UDP (DPT 1.001) | cbsigma | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group read/response over UDP (DPT 9.001) | cbsigma | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure device management: serial number (user 1) | cbsigma | calimero-server | UNSUPPORTED | no device management on the client |
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
| secure session connect (user 2, bound address) | cbsigma | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| secure tunnel group read/response (DPT 9.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| plain connection refused by the secure server | xknx | calimero-server | PASS |  |
| secure routing | knxultimate | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing | knxd | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing write (DPT 1.001) | xknx | calimero-tools | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | xknx | calimero-tools | PASS |  |
| secure routing write (DPT 1.001) | xknx | cbsigma | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | xknx | cbsigma | PASS |  |
| secure routing write (DPT 1.001) | calimero-tools | xknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | xknx | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device; xknx does not act as one, and the pairing has no surrogate on the network. Towards a system under test with the surrogate capability, it passes. (observed: 20:13:29.671 [ERROR  ] io.calimero.tools.ProcComm: compl |
| secure routing write (DPT 1.001) | calimero-tools | cbsigma | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | cbsigma | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device; cB-Sigma knx does not act as one ("no device toolkey"), as with xknx (calimero-tools-data-secure-routing). (observed: 20:13:59.483 [ERROR  ] io.calimero.tools.ProcComm: completed with error io.calimero.secure.Knx |
| secure routing write (DPT 1.001) | cbsigma | xknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | cbsigma | xknx | PASS |  |
| secure routing write (DPT 1.001) | cbsigma | calimero-tools | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | cbsigma | calimero-tools | PASS |  |
| server secure routing | - | knxd | UNSUPPORTED | no secure routing in the server |
| secure routing into the server, seen by a secure tunnel | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| secure routing into the server, seen by a secure tunnel | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure routing into the server, seen by a secure tunnel | cbsigma | calimero-server | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | xknx | calimero-server | PASS | observer/responder calimero-tools.  |
| secure routing out of the server, from a secure tunnel | xknx | calimero-server | PASS | observer/responder cbsigma.  |

## management

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| remote property services | - | knxd | UNSUPPORTED | no remote device management on the server |
| remote property read: friendly name (A_PropertyValue_Read) | xknx | calimero-server | UNSUPPORTED | xknx's management answers come only in transport connections |
| remote property read in a transport connection | xknx | calimero-server | PASS |  |
| remote property write, then read back (A_PropertyValue_Write) | xknx | calimero-server | PASS |  |
| tool access read: S-A_Sync, then S-A_Data (tool key) | xknx | calimero-server | UNSUPPORTED | no tool key access on the server |
| tool access read in a transport connection | xknx | calimero-server | UNSUPPORTED | no tool key access on the server |
| tool access write (S-A_Data, tool key) | xknx | calimero-server | UNSUPPORTED | no tool key access on the server |
| plain management refused by a secured device | xknx | calimero-server | UNSUPPORTED | no tool key access on the server |
| remote property services | knxultimate | calimero-server | UNSUPPORTED | no remote device management on the client |
| remote property services | knxd | calimero-server | UNSUPPORTED | no remote device management on the client |
| remote property read: friendly name (A_PropertyValue_Read) | calimero-tools | calimero-server | PASS |  |
| remote property read in a transport connection | calimero-tools | calimero-server | PASS |  |
| remote property write, then read back (A_PropertyValue_Write) | calimero-tools | calimero-server | PASS |  |
| tool access read: S-A_Sync, then S-A_Data (tool key) | calimero-tools | calimero-server | UNSUPPORTED | no tool key access on the server |
| tool access read in a transport connection | calimero-tools | calimero-server | UNSUPPORTED | no tool key access on the server |
| tool access write (S-A_Data, tool key) | calimero-tools | calimero-server | UNSUPPORTED | no tool key access on the server |
| plain management refused by a secured device | calimero-tools | calimero-server | UNSUPPORTED | no tool key access on the server |
| remote property services | cbsigma | calimero-server | UNSUPPORTED | no remote device management on the client |

## sim

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| knx-sim: tunnel write reaches the bus (UDP) | xknx | cbsigma | PASS |  |
| knx-sim: tunnel read answered (UDP, DPT 9.001) | xknx | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (TCP) | xknx | cbsigma | PASS |  |
| knx-sim: tunnel read answered (TCP, DPT 9.001) | xknx | cbsigma | PASS |  |
| knx-sim: repeated indication delivered once (UDP) | xknx | cbsigma | PASS |  |
| knx-sim: unacknowledged request reported as failed (UDP) | xknx | cbsigma | KNOWN-DIFFERENCE | xknx 4.1.1 repeats the TUNNELLING_REQUEST once and closes the tunnel ("Sending TunnellingRequest failed twice"), as the standard asks, but its telegram queue only logs the CommunicationError ("Could not send CEMI frame"), so the adapter's write, like any xknx application, cannot see that nothing was |
| knx-sim: secure tunnel write (user 2) | xknx | cbsigma | PASS |  |
| knx-sim: secure tunnel read answered (user 2) | xknx | cbsigma | PASS |  |
| knx-sim: Data Secure write opened by the gateway | xknx | cbsigma | PASS |  |
| knx-sim: Data Secure response of the gateway opened | xknx | cbsigma | PASS |  |
| knx-sim: replayed secure wrapper discarded | xknx | cbsigma | PASS |  |
| knx-sim: tampered secure wrapper discarded | xknx | cbsigma | PASS |  |
| knx-sim: SESSION_STATUS close ends the session | xknx | cbsigma | PASS |  |
| knx-sim router: ROUTING_BUSY holds back the answer (500 ms) | xknx | cbsigma | PASS |  |
| knx-sim router: answering goes on after ROUTING_LOST_MESSAGE | xknx | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (UDP) | knxultimate | cbsigma | PASS |  |
| knx-sim: tunnel read answered (UDP, DPT 9.001) | knxultimate | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (TCP) | knxultimate | cbsigma | PASS |  |
| knx-sim: tunnel read answered (TCP, DPT 9.001) | knxultimate | cbsigma | PASS |  |
| knx-sim: repeated indication delivered once (UDP) | knxultimate | cbsigma | PASS |  |
| knx-sim: unacknowledged request reported as failed (UDP) | knxultimate | cbsigma | KNOWN-DIFFERENCE | KNXUltimate 6.3.2's KNXClient.write returns void (fire and forget): the adapter, like any KNXUltimate application, cannot tell a write the gateway never acknowledged from one it did (observed: the write was reported as sent; knx-sim acknowledged nothing) |
| knx-sim: secure tunnel write (user 2) | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: secure tunnel read answered (user 2) | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: Data Secure write opened by the gateway | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: Data Secure response of the gateway opened | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: replayed secure wrapper discarded | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: tampered secure wrapper discarded | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: SESSION_STATUS close ends the session | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: idle secure session kept alive past 60 s | knxultimate | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim router: ROUTING_BUSY holds back the answer (500 ms) | knxultimate | cbsigma | KNOWN-DIFFERENCE | KNXUltimate 6.3.2 reports a received ROUTING_BUSY as an error event and keeps sending: it answered 5 ms after a ROUTING_BUSY with wait time 500 ms (KNXnet/IP routing flow control asks for a pause of at least the wait time) (observed: answered 5 ms after a ROUTING_BUSY with wait time 500 ms) |
| knx-sim router: answering goes on after ROUTING_LOST_MESSAGE | knxultimate | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (UDP) | knxd | cbsigma | PASS |  |
| knx-sim: tunnel read answered (UDP, DPT 9.001) | knxd | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (TCP) | knxd | cbsigma | UNSUPPORTED | no TCP |
| knx-sim: tunnel read answered (TCP, DPT 9.001) | knxd | cbsigma | UNSUPPORTED | no TCP |
| knx-sim: repeated indication delivered once (UDP) | knxd | cbsigma | PASS |  |
| knx-sim: unacknowledged request reported as failed (UDP) | knxd | cbsigma | PASS |  |
| knx-sim: secure tunnel write (user 2) | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: secure tunnel read answered (user 2) | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: Data Secure write opened by the gateway | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: Data Secure response of the gateway opened | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: replayed secure wrapper discarded | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: tampered secure wrapper discarded | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: SESSION_STATUS close ends the session | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim: idle secure session kept alive past 60 s | knxd | cbsigma | UNSUPPORTED | no KNX IP Secure client |
| knx-sim router: ROUTING_BUSY holds back the answer (500 ms) | knxd | cbsigma | KNOWN-DIFFERENCE | knxd 0.14.73 defines ROUTING_BUSY (src/libserver/eibnetip.h) but its router backend does not act on a received one: it answered 31 to 114 ms after a ROUTING_BUSY with wait time 500 ms (observed: answered 60 ms after a ROUTING_BUSY with wait time 500 ms) |
| knx-sim router: answering goes on after ROUTING_LOST_MESSAGE | knxd | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (UDP) | calimero-tools | cbsigma | PASS |  |
| knx-sim: tunnel read answered (UDP, DPT 9.001) | calimero-tools | cbsigma | PASS |  |
| knx-sim: tunnel write reaches the bus (TCP) | calimero-tools | cbsigma | PASS |  |
| knx-sim: tunnel read answered (TCP, DPT 9.001) | calimero-tools | cbsigma | PASS |  |
| knx-sim: repeated indication delivered once (UDP) | calimero-tools | cbsigma | PASS |  |
| knx-sim: unacknowledged request reported as failed (UDP) | calimero-tools | cbsigma | PASS |  |
| knx-sim: secure tunnel write (user 2) | calimero-tools | cbsigma | PASS |  |
| knx-sim: secure tunnel read answered (user 2) | calimero-tools | cbsigma | PASS |  |
| knx-sim: Data Secure write opened by the gateway | calimero-tools | cbsigma | KNOWN-DIFFERENCE | the same cause as calimero-tools-data-secure-tunnel: calimero-tools 3.0-M1 send and read Data Secure groups only through a surrogate device with a tool key ("no device toolkey for 0.0.0"); knx-sim has none on its bus (observed: 20:18:15.747 [ERROR  ] io.calimero.tools.ProcComm: completed with error  |
| knx-sim: Data Secure response of the gateway opened | calimero-tools | cbsigma | KNOWN-DIFFERENCE | the same cause as calimero-tools-data-secure-tunnel: calimero-tools 3.0-M1 send and read Data Secure groups only through a surrogate device with a tool key ("no device toolkey for 0.0.0"); knx-sim has none on its bus (observed: 20:18:17.744 [INFO   ] io.calimero.knxnetip.KNX IP 🔒 Tunneling 172.20.0. |
| knx-sim: replayed secure wrapper discarded | calimero-tools | cbsigma | PASS |  |
| knx-sim: tampered secure wrapper discarded | calimero-tools | cbsigma | PASS |  |
| knx-sim: SESSION_STATUS close ends the session | calimero-tools | cbsigma | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 (calimero-core 3.0-M1) keeps its tunnel and TCP connection after the gateway's SESSION_STATUS close: 18 s later knx-sim still had the channel, and the tool logged nothing; the status is known to the code (statusMsg) but a close from the server is not acted on (observed: 3 s aft |
| knx-sim router: ROUTING_BUSY holds back the answer (500 ms) | calimero-tools | cbsigma | UNSUPPORTED | no routing group responder |
| knx-sim router: answering goes on after ROUTING_LOST_MESSAGE | calimero-tools | cbsigma | UNSUPPORTED | no routing group responder |
| knx-sim: idle secure session kept alive past 60 s | xknx | cbsigma | PASS |  |
| knx-sim: idle secure session kept alive past 60 s | calimero-tools | cbsigma | PASS |  |

## files

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| keyring: the test profile (scripts/secure-fixture.py) | xknx | - | UNSUPPORTED | no keyring operation |
| keyring: the test profile (scripts/secure-fixture.py) | knxultimate | - | UNSUPPORTED | no keyring operation |
| keyring: the test profile (scripts/secure-fixture.py) | knxd | - | UNSUPPORTED | no keyring operation |
| keyring: the test profile (scripts/secure-fixture.py) | calimero-tools | - | UNSUPPORTED | no keyring operation |
| keyring: the test profile (scripts/secure-fixture.py) | cbsigma | fixture | PASS |  |
| keyring: the test profile written by knx-sim | cbsigma | cbsigma | PASS |  |
| keyring: wrong password refused | cbsigma | - | PASS |  |
