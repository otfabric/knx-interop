# knx-interop results

Started 2026-10-29T21:21:58.887924+00:00, finished 2026-10-29T21:30:36.240074+00:00 on darwin/arm64.

Summary: known-difference 4, pass 361, unsupported 42

## Implementations

| Adapter | Implementation | Version | Roles |
|---|---|---|---|
| calimero-server | calimero-server | 3.0-M1 | server |
| calimero-tools | calimero | 3.0-M1 | client |
| goknx | go-knx | (devel) (knxctl v0.1.1+dirty) | server, client |
| knxd | knxd | 0.14.73 | server, client |
| knxultimate | knxultimate | 6.3.1 | client |
| probe | probe | 1.0 | client |
| xknx | xknx | 4.0.0 | client |

## tunnel

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| discover (multicast search) | goknx | goknx | PASS |  |
| describe | goknx | goknx | PASS |  |
| connect and disconnect | goknx | goknx | PASS |  |
| group write (DPT 1.001) | goknx | goknx | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | goknx | goknx | PASS | observer/responder xknx.  |
| discover (multicast search) | xknx | goknx | PASS |  |
| describe | xknx | goknx | PASS |  |
| connect and disconnect | xknx | goknx | PASS |  |
| group write (DPT 1.001) | xknx | goknx | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | xknx | goknx | PASS | observer/responder goknx.  |
| discover (multicast search) | knxultimate | goknx | PASS |  |
| describe | knxultimate | goknx | KNOWN-DIFFERENCE | KNXUltimate 6.3.1 announces <local IP>:3671 in its DESCRIPTION_REQUEST HPAI while it listens on an ephemeral port (src/KNXClient.ts sendDescriptionRequestMessage: new HPAI(localIPAddress), default port 3671); servers that answer to the HPAI, as the standard requires, answer a port nobody listens on. |
| connect and disconnect | knxultimate | goknx | PASS |  |
| group write (DPT 1.001) | knxultimate | goknx | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxultimate | goknx | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | goknx | PASS |  |
| describe | calimero-tools | goknx | PASS |  |
| connect and disconnect | calimero-tools | goknx | PASS |  |
| group write (DPT 1.001) | calimero-tools | goknx | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | calimero-tools | goknx | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | goknx | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | goknx | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | goknx | PASS |  |
| group write (DPT 1.001) | knxd | goknx | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxd | goknx | PASS | observer/responder xknx.  |
| discover (multicast search) | goknx | knxd | PASS |  |
| describe | goknx | knxd | PASS |  |
| connect and disconnect | goknx | knxd | PASS |  |
| group write (DPT 1.001) | goknx | knxd | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | goknx | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | xknx | knxd | PASS |  |
| describe | xknx | knxd | PASS |  |
| connect and disconnect | xknx | knxd | PASS |  |
| group write (DPT 1.001) | xknx | knxd | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | xknx | knxd | PASS | observer/responder goknx.  |
| discover (multicast search) | knxultimate | knxd | PASS |  |
| describe | knxultimate | knxd | KNOWN-DIFFERENCE | KNXUltimate 6.3.1 announces <local IP>:3671 in its DESCRIPTION_REQUEST HPAI while it listens on an ephemeral port (src/KNXClient.ts sendDescriptionRequestMessage: new HPAI(localIPAddress), default port 3671); servers that answer to the HPAI, as the standard requires, answer a port nobody listens on. |
| connect and disconnect | knxultimate | knxd | PASS |  |
| group write (DPT 1.001) | knxultimate | knxd | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxultimate | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | knxd | PASS |  |
| describe | calimero-tools | knxd | PASS |  |
| connect and disconnect | calimero-tools | knxd | PASS |  |
| group write (DPT 1.001) | calimero-tools | knxd | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | calimero-tools | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | knxd | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | knxd | PASS |  |
| group write (DPT 1.001) | knxd | knxd | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxd | knxd | PASS | observer/responder xknx.  |
| discover (multicast search) | goknx | calimero-server | PASS |  |
| describe | goknx | calimero-server | PASS |  |
| connect and disconnect | goknx | calimero-server | PASS |  |
| group write (DPT 1.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| group read/response (DPT 9.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | xknx | calimero-server | PASS |  |
| describe | xknx | calimero-server | PASS |  |
| connect and disconnect | xknx | calimero-server | PASS |  |
| group write (DPT 1.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| discover (multicast search) | knxultimate | calimero-server | PASS |  |
| describe | knxultimate | calimero-server | PASS |  |
| connect and disconnect | knxultimate | calimero-server | PASS |  |
| group write (DPT 1.001) | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | calimero-tools | calimero-server | PASS |  |
| describe | calimero-tools | calimero-server | PASS |  |
| connect and disconnect | calimero-tools | calimero-server | PASS |  |
| group write (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | calimero-tools | calimero-server | PASS | observer/responder xknx.  |
| discover (multicast search) | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| describe | knxd | calimero-server | UNSUPPORTED | The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data. |
| connect and disconnect | knxd | calimero-server | PASS |  |
| group write (DPT 1.001) | knxd | calimero-server | PASS | observer/responder goknx.  |
| group read/response (DPT 9.001) | knxd | calimero-server | PASS | observer/responder xknx.  |

## dpt

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| DPT 1.001 on | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 1.001 off | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 5.001 100 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 5.010 200 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | goknx | goknx | PASS | observer/responder xknx.  |
| DPT 1.001 on | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 off | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 5.001 100 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 5.010 200 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | xknx | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxultimate | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 on | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 off | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 5.001 100 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 5.010 200 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | calimero-tools | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxd | goknx | PASS | observer/responder goknx.  |
| DPT 1.001 on | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 off | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 5.001 100 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 5.010 200 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | goknx | knxd | PASS | observer/responder xknx.  |
| DPT 1.001 on | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 off | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 5.001 100 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 5.010 200 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | xknx | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxultimate | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 on | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 off | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 5.001 100 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 5.010 200 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | calimero-tools | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxd | knxd | PASS | observer/responder goknx.  |
| DPT 1.001 on | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 off | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.001 100 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 5.010 200 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 7.001 4660 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 21.5 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.001 -30 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 9.004 1200 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 12.001 305419896 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 13.001 -2 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 14.056 1234.5 | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 16.000 KNX interop | goknx | calimero-server | PASS | observer/responder xknx.  |
| DPT 1.001 on | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 off | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.001 100 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.010 200 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | xknx | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 on | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 off | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.001 100 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.010 200 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 on | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 1.001 off | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.001 100 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 5.010 200 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 7.001 4660 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 21.5 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.001 -30 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 9.004 1200 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 12.001 305419896 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 13.001 -2 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 14.056 1234.5 | knxd | calimero-server | PASS | observer/responder goknx.  |
| DPT 16.000 KNX interop | knxd | calimero-server | PASS | observer/responder goknx.  |

## v2

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| group write over TCP (DPT 1.001) | goknx | goknx | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | goknx | goknx | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | goknx | goknx | PASS |  |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | goknx | goknx | PASS | observer/responder xknx.  |
| group write over TCP (DPT 1.001) | xknx | goknx | PASS | observer/responder goknx.  |
| group read over TCP (DPT 9.001) | xknx | goknx | PASS | observer/responder goknx.  |
| device management: device serial number (M_PropRead) | xknx | goknx | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | xknx | goknx | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxultimate | goknx | PASS | observer/responder goknx.  |
| group read over TCP (DPT 9.001) | knxultimate | goknx | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | knxultimate | goknx | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxultimate | goknx | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | goknx | PASS | observer/responder goknx.  |
| group read over TCP (DPT 9.001) | calimero-tools | goknx | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | calimero-tools | goknx | PASS |  |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | goknx | PASS | observer/responder goknx.  |
| group write over TCP (DPT 1.001) | knxd | goknx | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | goknx | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | goknx | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | goknx | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | goknx | knxd | UNSUPPORTED | no TCP on the server |
| group read over TCP (DPT 9.001) | goknx | knxd | UNSUPPORTED | no TCP on the server |
| device management: device serial number (M_PropRead) | goknx | knxd | UNSUPPORTED | no device management on the server |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | goknx | knxd | PASS | observer/responder xknx.  |
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
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | calimero-tools | knxd | PASS | observer/responder goknx.  |
| group write over TCP (DPT 1.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| group read over TCP (DPT 9.001) | knxd | knxd | UNSUPPORTED | no TCP on the client |
| device management: device serial number (M_PropRead) | knxd | knxd | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxd | knxd | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| group read over TCP (DPT 9.001) | goknx | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | goknx | calimero-server | PASS |  |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | goknx | calimero-server | UNSUPPORTED | no busmonitor on the server |
| group write over TCP (DPT 1.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| group read over TCP (DPT 9.001) | xknx | calimero-server | PASS | observer/responder goknx.  |
| device management: device serial number (M_PropRead) | xknx | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | xknx | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | knxultimate | calimero-server | PASS | observer/responder goknx.  |
| group read over TCP (DPT 9.001) | knxultimate | calimero-server | PASS | observer/responder xknx.  |
| device management: device serial number (M_PropRead) | knxultimate | calimero-server | UNSUPPORTED | no device management on the client |
| busmonitor sees a write (L_Busmon.ind, TP1 frame) | knxultimate | calimero-server | UNSUPPORTED | no busmonitor on the client |
| group write over TCP (DPT 1.001) | calimero-tools | calimero-server | PASS | observer/responder goknx.  |
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
| heartbeat on an open channel → E_NO_ERROR | probe | goknx | PASS | status 0x00 after 0.0 s |
| TUNNELLING_REQUEST sequence 0 acknowledged | probe | goknx | PASS | ack status 0 |
| repeated sequence 0 acknowledged again (duplicate) | probe | goknx | PASS | ack status 0 |
| out-of-order sequence 5 not acknowledged | probe | goknx | PASS | ack status None |
| sequence numbers roll over 255 → 0 | probe | goknx | PASS | 259 requests acknowledged |
| DISCONNECT_REQUEST → E_NO_ERROR | probe | goknx | PASS | DISCONNECT_RESPONSE |
| heartbeat after disconnect → E_CONNECTION_ID | probe | goknx | PASS | status 0x21 |
| survives header length 7 | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives protocol version 0x20 | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length longer than the datagram | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives total length shorter than the datagram | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives truncated header | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives unknown service type 0x0F00 | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives HPAI of length 7 | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives 2000-octet datagram | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives empty CONNECT_REQUEST | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| survives CRI length 0 | probe | goknx | PASS | answers DESCRIPTION_REQUEST afterwards |
| CONNECTIONSTATE_REQUEST of an unknown channel → E_CONNECTION_ID | probe | goknx | PASS | status 0x21 |
| unsupported connection type → E_CONNECTION_TYPE | probe | goknx | PASS | status 0x22 |
| raw tunnelling layer → refused | probe | goknx | PASS | observed: status 0x29 |
| TCP HPAI over UDP → refused | probe | goknx | PASS | observed: status 0x01 |
| heartbeat right after the malformed datagrams | probe | goknx | PASS | observed: status 0x00 after 0.0 s |
| channel exhaustion → E_NO_MORE_CONNECTIONS | probe | goknx | PASS | 8 connections, then status 0x24 |
| still serving after the tests | probe | goknx | PASS | answers DESCRIPTION_REQUEST |
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
| heartbeat right after the malformed datagrams | probe | calimero-server | PASS | observed: status 0x27 after 0.0 s |
| channel exhaustion → E_NO_MORE_CONNECTIONS | probe | calimero-server | PASS | 8 connections, then status 0x24 |
| still serving after the tests | probe | calimero-server | PASS | answers DESCRIPTION_REQUEST |

## routing

| Scenario | Client | Peer | Result | Detail |
|---|---|---|---|---|
| routing write (multicast) | goknx | xknx | PASS |  |
| routing write (multicast) | goknx | knxultimate | PASS |  |
| routing write (multicast) | goknx | calimero-tools | PASS |  |
| routing write (multicast) | goknx | knxd | PASS |  |
| routing write (multicast) | xknx | goknx | PASS |  |
| routing write (multicast) | xknx | knxultimate | PASS |  |
| routing write (multicast) | xknx | calimero-tools | PASS |  |
| routing write (multicast) | xknx | knxd | PASS |  |
| routing write (multicast) | knxultimate | goknx | PASS |  |
| routing write (multicast) | knxultimate | xknx | PASS |  |
| routing write (multicast) | knxultimate | calimero-tools | PASS |  |
| routing write (multicast) | knxultimate | knxd | PASS |  |
| routing write (multicast) | calimero-tools | goknx | PASS |  |
| routing write (multicast) | calimero-tools | xknx | PASS |  |
| routing write (multicast) | calimero-tools | knxultimate | PASS |  |
| routing write (multicast) | calimero-tools | knxd | PASS |  |
| routing write (multicast) | knxd | goknx | PASS |  |
| routing write (multicast) | knxd | xknx | PASS |  |
| routing write (multicast) | knxd | knxultimate | PASS |  |
| routing write (multicast) | knxd | calimero-tools | PASS |  |
