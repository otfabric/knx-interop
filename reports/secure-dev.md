# knx-interop results

Started 2026-10-30T00:37:18.818221+00:00, finished 2026-10-30T00:43:44.146926+00:00 on darwin/arm64.

Summary: fail 6, known-difference 3, pass 56, unsupported 16

## Implementations

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| calimero-server | calimero-server | 3.0-M1 | server |
| calimero-tools | calimero | 3.0-M1 | client |
| goknx | go-knx | (devel) (knxctl v0.3.0+dirty) | server, client |
| knxd | knxd | 0.14.73 | server, client |
| knxultimate | knxultimate | 6.3.1 | client |
| xknx | xknx | 4.0.0 | client |

## secure

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| secure session connect (user 2, bound address) | goknx | goknx | PASS |  |
| secure tunnel group write (DPT 1.001) | goknx | goknx | PASS | observer/responder xknx.  |
| secure tunnel group read/response (DPT 9.001) | goknx | goknx | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | goknx | goknx | PASS | observer/responder xknx.  |
| secure session over UDP (user 2) | goknx | goknx | PASS |  |
| secure group write over UDP (DPT 1.001) | goknx | goknx | PASS | observer/responder xknx.  |
| secure group read/response over UDP (DPT 9.001) | goknx | goknx | PASS | observer/responder xknx.  |
| secure device management: serial number (user 1) | goknx | goknx | PASS |  |
| secure session connect (user 2, bound address) | xknx | goknx | PASS |  |
| secure tunnel group write (DPT 1.001) | xknx | goknx | PASS | observer/responder goknx.  |
| secure tunnel group read/response (DPT 9.001) | xknx | goknx | PASS | observer/responder goknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | xknx | goknx | PASS | observer/responder goknx.  |
| secure session over UDP (user 2) | xknx | goknx | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group write over UDP (DPT 1.001) | xknx | goknx | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group read/response over UDP (DPT 9.001) | xknx | goknx | UNSUPPORTED | no secure sessions over UDP on the client |
| secure device management: serial number (user 1) | xknx | goknx | UNSUPPORTED | no device management on the client |
| secure tunnelling | knxultimate | goknx | UNSUPPORTED | no KNX IP Secure client |
| secure session connect (user 2, bound address) | calimero-tools | goknx | PASS |  |
| secure tunnel group write (DPT 1.001) | calimero-tools | goknx | PASS | observer/responder goknx.  |
| secure tunnel group read/response (DPT 9.001) | calimero-tools | goknx | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | calimero-tools | goknx | KNOWN-DIFFERENCE | observer/responder goknx. calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device (S-A_Sync and group object diagnostics with the surrogate's tool key) and require every sender of the group in the keyring to be such a device; the profile's tunnel groups list the tunnel |
| secure session over UDP (user 2) | calimero-tools | goknx | PASS |  |
| secure group write over UDP (DPT 1.001) | calimero-tools | goknx | PASS | observer/responder goknx.  |
| secure group read/response over UDP (DPT 9.001) | calimero-tools | goknx | PASS | observer/responder xknx.  |
| secure device management: serial number (user 1) | calimero-tools | goknx | PASS |  |
| secure tunnelling | knxd | goknx | UNSUPPORTED | no KNX IP Secure client |
| plain connection refused by the secure server | goknx | goknx | PASS |  |
| secure tunnelling server | - | knxd | UNSUPPORTED | no KNX IP Secure server |
| secure session connect (user 2, bound address) | goknx | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure tunnel group read/response (DPT 9.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure session over UDP (user 2) | goknx | calimero-server | PASS |  |
| secure group write over UDP (DPT 1.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure group read/response over UDP (DPT 9.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure device management: serial number (user 1) | goknx | calimero-server | PASS |  |
| secure session connect (user 2, bound address) | xknx | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| secure tunnel group read/response (DPT 9.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| secure session over UDP (user 2) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group write over UDP (DPT 1.001) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure group read/response over UDP (DPT 9.001) | xknx | calimero-server | UNSUPPORTED | no secure sessions over UDP on the client |
| secure device management: serial number (user 1) | xknx | calimero-server | UNSUPPORTED | no device management on the client |
| secure tunnelling | knxultimate | calimero-server | UNSUPPORTED | no KNX IP Secure client |
| secure session connect (user 2, bound address) | calimero-tools | calimero-server | PASS |  |
| secure tunnel group write (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| secure tunnel group read/response (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| Data Secure group write through a secure tunnel (DPT 9.001) | calimero-tools | calimero-server | KNOWN-DIFFERENCE | observer/responder goknx. calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device (S-A_Sync and group object diagnostics with the surrogate's tool key) and require every sender of the group in the keyring to be such a device; the profile's tunnel groups list the tunnel |
| secure session over UDP (user 2) | calimero-tools | calimero-server | PASS |  |
| secure group write over UDP (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| secure group read/response over UDP (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| secure device management: serial number (user 1) | calimero-tools | calimero-server | PASS |  |
| secure tunnelling | knxd | calimero-server | UNSUPPORTED | no KNX IP Secure client |
| plain connection refused by the secure server | goknx | calimero-server | PASS |  |
| secure routing | knxultimate | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing | knxd | - | UNSUPPORTED | no KNX IP Secure routing |
| secure routing write (DPT 1.001) | goknx | xknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | goknx | xknx | PASS |  |
| secure routing write (DPT 1.001) | goknx | calimero-tools | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | goknx | calimero-tools | PASS |  |
| secure routing write (DPT 1.001) | xknx | goknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | xknx | goknx | PASS |  |
| secure routing write (DPT 1.001) | xknx | calimero-tools | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | xknx | calimero-tools | PASS |  |
| secure routing write (DPT 1.001) | calimero-tools | goknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | goknx | PASS |  |
| secure routing write (DPT 1.001) | calimero-tools | xknx | PASS |  |
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | xknx | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device; xknx does not act as one, and the pairing has no go-knx on the network. Towards go-knx, the surrogate, it passes. (observed: 00:40:47.908 [ERROR  ] io.calimero.tools.ProcComm: completed with error io.calimero.sec |
| secure routing into the server, seen by a secure tunnel | xknx | goknx | PASS | observer/responder goknx.  |
| secure routing into the server, seen by a secure tunnel | calimero-tools | goknx | PASS | observer/responder goknx.  |
| secure routing out of the server, from a secure tunnel | xknx | goknx | PASS | observer/responder goknx.  |
| secure routing out of the server, from a secure tunnel | goknx | goknx | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | goknx | goknx | PASS | observer/responder calimero-tools.  |
| server secure routing | - | knxd | UNSUPPORTED | no secure routing in the server |
| secure routing into the server, seen by a secure tunnel | goknx | calimero-server | FAIL | observer/responder xknx. observer xknx saw {'telegrams': []} received 0 of 1 telegrams |
| secure routing into the server, seen by a secure tunnel | xknx | calimero-server | FAIL | observer/responder goknx. observer goknx saw {'telegrams': []} received 0 of 1 telegrams |
| secure routing into the server, seen by a secure tunnel | calimero-tools | calimero-server | FAIL | observer/responder goknx. observer goknx saw {'telegrams': []} received 0 of 1 telegrams |
| secure routing out of the server, from a secure tunnel | xknx | calimero-server | FAIL | observer/responder goknx. router goknx saw {'telegrams': []} received 0 of 1 telegrams |
| secure routing out of the server, from a secure tunnel | goknx | calimero-server | FAIL | observer/responder xknx. router xknx saw {'telegrams': []} received 0 of 1 telegrams |
| secure routing out of the server, from a secure tunnel | goknx | calimero-server | FAIL | observer/responder calimero-tools. router calimero-tools saw {'telegrams': []} received 0 of 1 telegrams:  |
