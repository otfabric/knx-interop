# Container contract (version 1.0)

Every adapter image runs one implementation and has the entry point
`/adapter/run`:

```text
run capabilities
run server [--routing] [--name NAME]
run client <op> [--target HOST] [--port 3671] [--nat] [--routing]
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
needs `--data`).

## server

Starts a KNXnet/IP server on UDP 0.0.0.0:3671 of the container (discovery
on, tunnelling with at least eight connections, `--routing` adds routing on
224.0.23.12:3671) with the friendly name NAME, and runs until it is
stopped. It prints `READY` on stderr when it starts; the runner waits until
the probe's DESCRIPTION_REQUEST is answered. The servers' virtual KNX
networks differ (calimero: an emulated subnet that answers reads with the
last written value; knxd: a dummy bus; go-knx: virtual devices with group
objects 1/0/1 (1.001), 1/0/2 (9.001 = 21.5), 1/0/3 (5.001), 1/0/4
(14.056), 1/0/5 (16.000)).

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
| `negative` (probe only) | the negative test suite against `--target` | `{"checks": [{"name", "status", "detail", "kind"}]}` |

`--data` carries the expected encoding of `--value` from the fixtures, for
adapters without a datapoint codec (knxd); adapters with a codec encode
the value themselves and the runner compares what an observer received with
the fixture.
