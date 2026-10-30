# Container contract (version 1.4)

Version 1.4 adds remote device management: the `remote-property`
operation (the remote property services of a device on the KNX network,
through a tunnel), `server --tool-access` (the server's device accepts only
management secured with its tool key, KNX Data Secure point to point), and
the `remoteProperty`, `toolAccess`, `server.remoteProperty` and
`server.toolAccess` capabilities. Version 1.3 added `--udp` (with `--secure`: the secure session over UDP),
`server --secure --routing` (the server's secure routing), the
`secureUdp`, `surrogate`, `server.secureUdp` and `server.secureRouting`
capabilities, and the profile's surrogate (15.15.255, a device with a tool
key) and surrogate group 1/3/3. Version 1.2 added `--secure` and `--user` (KNX IP Secure and KNX Data Secure
with the test profile below) and the `secure`, `dataSecure` and
`server.secure` capabilities. Version 1.1 added `--tcp`, the `property` and
`busmonitor` operations and the `server` capabilities. Adapters of earlier
versions stay valid.

Every adapter image runs one implementation and has the entry point
`/adapter/run`:

```text
run capabilities
run server [--routing] [--name NAME] [--secure] [--tool-access]
run client <op> [--target HOST] [--port 3671] [--nat] [--routing] [--tcp]
                [--secure] [--user 1|2|3] [--udp]
                [--object TYPE] [--pid PID]
                [--group G] [--dpt D] [--value V] [--data HEX]
                [--count N] [--timeout SECONDS]
                [--device IA] [--start N] [--connected] [--tool-access]
```

## capabilities

One JSON document on stdout:

```json
{"schemaVersion": "1.0", "implementation": "xknx", "version": "4.0.0",
 "roles": ["client"], "features": {"discover": true, "describe": true, "tunnel": true,
 "routing": true, "nat": true, "answer": true, "secure": false}, "notes": "..."}
```

Features a runner relies on: `discover`, `describe`, `tunnel`, `routing`,
`nat`, `answer` (group read responder), `dptCodec` (false: the adapter
needs `--data`), and since 1.1 `tcp`, `property`, `busmonitor` for the
client and, under `server`, `tcp`, `property` (device management) and
`busmonitor` (a busmonitor connection sees the writes of a tunnel at the same
time) for the server role; since 1.2 `secure` (KNX IP Secure: secure
tunnelling and, with `--routing`, secure routing), `dataSecure` (KNX Data
Secure group communication) and `server.secure`; since 1.4
`remoteProperty` and `toolAccess` for the client and `server.remoteProperty`
and `server.toolAccess` for the server role.

## KNX Secure test profile (1.2)

Every image carries the profile in `/adapter/common/secure` (from
`adapters/common/secure`, written by `scripts/secure-fixture.py`, `make
fixture`). **All of its
keys and passwords are public test values.**

| Item | Value |
|---|---|
| Keyring | `knx-interop.knxkeys`, password `knx-interop` |
| Host (server) | 1.1.0, device authentication password `knx-interop-device` |
| Users | 1 management (`knx-interop-user1`); 2 → tunnelling address 1.1.10 (`knx-interop-user2`); 3 → 1.1.11 (`knx-interop-user3`) |
| Backbone key (secure routing) | `6b6e782d696e7465726f702d6b657921`, latency 1000 ms |
| Data Secure groups | 1/3/1 and 1/3/2, senders 1.1.10–1.1.17, 15.15.240 (Calimero tools), 15.15.250 (xknx), 15.15.255 (go-knx) |
| Surrogate (1.3) | 15.15.255, the routing source of a system under test that offers the `surrogate` capability (go-knx): a device with a tool key; the only sender of Data Secure group 1/3/3, which Calimero tools write through it (Calimero requires every sender of a group to be a device and picks its surrogate among them) |
| Calimero server | the same profile as a keyfile, `calimero.keyfile` |
| Tool keys (1.4) | the keyring's devices 1.1.0 (the server's device), 15.15.255 and 15.15.240 have tool keys; `--tool-access` uses the one of 1.1.0 |

With `--secure` a client opens a secure session over TCP as user `--user`
(default 2) and verifies the server's device authentication code, or with
`--routing` routes with the backbone key; in both cases it applies Data
Secure to the profile's groups (plain groups stay plain). A server started
with `--secure` refuses plain tunnelling and device management, serves
users 1–3 (user 1: device management) and binds users 2 and 3 to their
addresses.

## Remote device management (1.4)

The server's own device, at its individual address 1.1.0, answers the
remote property services sent through a tunnel (A_PropertyValue_Read,
_Write and _Response, A_PropertyDescription_Read), connectionless and in a
transport layer connection (T_Connect, numbered data with T_ACK,
T_Disconnect). A server started with `--tool-access` secures them with
the device's tool key: it answers only S-A_Sync_Req and S-A_Data with tool
access, and plain requests get no answer.

`remote-property` addresses the object by its type: the adapter finds its
index in the device's interface object list (device object, PID 71), as a
tool does, and reads `--count` elements of `--pid` from element `--start`
(default 1), or with `--data` writes them and reports the device's answer
(the elements after the write). `--connected` uses a transport connection;
`--tool-access` synchronises (S-A_Sync) and secures the access with the
tool key of `--device` (default 1.1.0) from the profile; `--secure` still
selects a secure tunnel. The runner reads and writes the friendly name of
the KNXnet/IP parameter object (type 11, PID 76).

## server

Starts a KNXnet/IP server on UDP 0.0.0.0:3671 of the container (discovery
on, tunnelling with at least eight connections, `--routing` adds routing on
224.0.23.12:3671) with the friendly name NAME, and runs until it is
stopped. It prints `READY` on stderr when it starts; the runner waits until
the probe's DESCRIPTION_REQUEST is answered. The servers' virtual KNX
networks differ (calimero: an emulated subnet that answers reads with the
last written value; knxd: a dummy bus; a system under test should offer
virtual devices with group objects 1/0/1 (1.001), 1/0/2 (9.001 = 21.5),
1/0/3 (5.001), 1/0/4 (14.056), 1/0/5 (16.000)).

## External adapters

knx-interop's own adapters are third-party stacks. A system under test
implements this contract in an image of its own and passes it to the
runner with `--adapter name=image` (`make matrix ADAPTER=name=image`): it
joins the server, client and routing roles its capabilities declare and is
preferred as observer and responder; `--gate name` fails the run only on
failures that involve it. The image needs the test profile at
`/adapter/common/secure` (it can copy it from a knx-interop image).

## client operations

Each operation prints exactly one result document as the last line of
stdout and exits 0 (pass), 1 (fail) or 3 (unsupported):

```json
{"schemaVersion": "1.0", "implementation": "...", "version": "...", "op": "read",
 "status": "pass", "durationMs": 1234, "data": {...}, "error": "..."}
```

| Operation | Does | `data` |
|---|---|---|
| `discover` | multicast SEARCH_REQUEST, collect for `--timeout` | `{"devices": [{"endpoint": "ip:port", "name", "address"}]}` |
| `describe` | DESCRIPTION_REQUEST to `--target` | `{"name", "address", "services": {"Core": 1, ...}}` |
| `connect` | open and close a tunnelling connection | `{"channel", "address"}` (as far as the implementation tells) |
| `write` | A_GroupValue_Write of `--value` with `--dpt` to `--group` (tunnel to `--target`, or `--routing`) | `{"data": "HEX"}` when known |
| `read` | A_GroupValue_Read; wait `--timeout` for the response | `{"source", "data": "HEX", "value"}` |
| `monitor` | listen until `--count` group telegrams or `--timeout`; prints `READY` on stderr once listening | `{"telegrams": [{"source", "group", "service": "write\|read\|response", "data"}]}` |
| `answer` | answer A_GroupValue_Read of `--group` with `--value` until `--count` answers or `--timeout`; `READY` on stderr | `{"answered": n}` |
| `property` (1.1) | device management (M_PropRead) of property `--pid` of interface object type `--object` | `{"data": "HEX"}` |
| `busmonitor` (1.1) | open a busmonitor connection, report `--count` L_Busmon.ind frames; `READY` on stderr | `{"frames": [{"raw": "HEX"}]}` (the TP1 frame) |
| `remote-property` (1.4) | remote property read (or with `--data` write) of `--device` through a tunnel to `--target` | `{"data": "HEX", "object": index}` |
| `negative` (probe only) | the negative test suite against `--target` | `{"checks": [{"name", "status", "detail", "kind"}]}` |

`--data` carries the expected encoding of `--value` from the fixtures, for
adapters without a datapoint codec (knxd); adapters with a codec encode
the value themselves and the runner compares what an observer received with
the fixture.
