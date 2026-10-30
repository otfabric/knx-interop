# Container contract (version 1.3)

Version 1.3 adds `--udp` (with `--secure`: the secure session over UDP),
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
run server [--routing] [--name NAME] [--secure]
run client <op> [--target HOST] [--port 3671] [--nat] [--routing] [--tcp]
                [--secure] [--user 1|2|3] [--udp]
                [--object TYPE] [--pid PID]
                [--group G] [--dpt D] [--value V] [--data HEX]
                [--count N] [--timeout SECONDS]
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
Secure group communication) and `server.secure`.

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

With `--secure` a client opens a secure session over TCP as user `--user`
(default 2) and verifies the server's device authentication code, or with
`--routing` routes with the backbone key; in both cases it applies Data
Secure to the profile's groups (plain groups stay plain). A server started
with `--secure` refuses plain tunnelling and device management, serves
users 1–3 (user 1: device management) and binds users 2 and 3 to their
addresses.

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
| `negative` (probe only) | the negative test suite against `--target` | `{"checks": [{"name", "status", "detail", "kind"}]}` |

`--data` carries the expected encoding of `--value` from the fixtures, for
adapters without a datapoint codec (knxd); adapters with a codec encode
the value themselves and the runner compares what an observer received with
the fixture.
