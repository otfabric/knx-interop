# knx-interop results

Started 2026-10-30T00:45:02.392746+00:00, finished 2026-10-30T00:48:17.801342+00:00 on darwin/arm64.

Summary: known-difference 2, pass 37, unsupported 8

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
| Data Secure group write over secure routing (DPT 9.001) | calimero-tools | xknx | KNOWN-DIFFERENCE | calimero-tools 3.0-M1 send Data Secure group telegrams only through a surrogate device; xknx does not act as one, and the pairing has no go-knx on the network. Towards go-knx, the surrogate, it passes. (observed: 00:47:41.260 [ERROR  ] io.calimero.tools.ProcComm: completed with error io.calimero.sec |
| secure routing into the server, seen by a secure tunnel | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure routing into the server, seen by a secure tunnel | xknx | calimero-server | PASS | observer/responder goknx.  |
| secure routing into the server, seen by a secure tunnel | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| secure routing out of the server, from a secure tunnel | xknx | calimero-server | PASS | observer/responder goknx.  |
| secure routing out of the server, from a secure tunnel | goknx | calimero-server | PASS | observer/responder xknx.  |
| secure routing out of the server, from a secure tunnel | goknx | calimero-server | PASS | observer/responder calimero-tools.  |
