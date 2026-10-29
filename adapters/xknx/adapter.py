#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""knx-interop adapter for xknx (XKNX/xknx, MIT): client roles only; xknx has
no KNXnet/IP server."""

import asyncio
import socket
import importlib.metadata
import sys

sys.path.insert(0, "/adapter/common")
import contract  # noqa: E402

from xknx import XKNX  # noqa: E402
from xknx.core.value_reader import ValueReader  # noqa: E402
from xknx.dpt import DPTArray, DPTBase, DPTBinary  # noqa: E402
from xknx.io import ConnectionConfig, ConnectionType, GatewayScanner  # noqa: E402
from xknx.io.self_description import request_description  # noqa: E402
from xknx.telegram import GroupAddress, Telegram  # noqa: E402
from xknx.telegram.apci import GroupValueRead, GroupValueResponse, GroupValueWrite  # noqa: E402

IMPL = "xknx"
VERSION = importlib.metadata.version("xknx")


def payload(dpt, value):
    t = DPTBase.parse_transcoder(dpt)
    if t is None:
        raise ValueError("xknx has no transcoder for DPT %s" % dpt)
    v = value
    if dpt.startswith("1."):
        v = value.lower() in ("1", "on", "true")
    elif dpt.startswith("16."):
        v = value
    else:
        v = float(value)
        if v == int(v) and not dpt.startswith(("9.", "14.")):
            v = int(v)
    return t.to_knx(v)


def hexdata(p):
    if isinstance(p, DPTBinary):
        return "%02X" % p.value
    if isinstance(p, DPTArray):
        return bytes(p.value).hex().upper()
    return ""


def service(p):
    if isinstance(p, GroupValueWrite):
        return "write"
    if isinstance(p, GroupValueResponse):
        return "response"
    if isinstance(p, GroupValueRead):
        return "read"
    return type(p).__name__


def config(a):
    if a.routing:
        return ConnectionConfig(connection_type=ConnectionType.ROUTING, local_ip=None)
    if a.tcp:
        return ConnectionConfig(connection_type=ConnectionType.TUNNELING_TCP, gateway_ip=a.target, gateway_port=a.port,
                                auto_reconnect=False)
    return ConnectionConfig(connection_type=ConnectionType.TUNNELING, gateway_ip=a.target, gateway_port=a.port,
                            route_back=a.nat, auto_reconnect=False)


def done(status, data=None, error=None):
    return status, data, error


async def run(a):
    if a.op == "discover":
        x = XKNX()
        found = await GatewayScanner(x, timeout_in_seconds=a.timeout).scan()
        devs = [{"endpoint": "%s:%d" % (g.ip_addr, g.port), "name": g.name, "address": str(g.individual_address)} for g in found]
        return done("pass", {"devices": devs})
    if a.op == "describe":
        g = await asyncio.wait_for(request_description(a.target, a.port, route_back=a.nat), a.timeout)
        services = {}
        if g.supports_tunnelling:
            services["Tunnelling"] = 2 if g.tunnelling_requires_secure is not None and g.supports_tunnelling_tcp else 1
        if g.supports_routing:
            services["Routing"] = 1
        return done("pass", {"name": g.name, "address": str(g.individual_address), "services": services})
    received = []
    got = asyncio.Event()

    def cb(t: Telegram):
        if not isinstance(t.destination_address, GroupAddress):
            return
        received.append(t)
        if len(received) >= a.count:
            got.set()

    x = XKNX(connection_config=config(a), daemon_mode=False, telegram_received_cb=None)
    await asyncio.wait_for(x.start(), a.timeout)
    try:
        if a.op == "connect":
            tun = x.knxip_interface._interface
            ch = getattr(tun, "communication_channel", None)
            ia = x.current_address
            return done("pass", {"channel": ch, "address": str(ia)})
        if a.op == "write":
            p = payload(a.dpt, a.value)
            await x.telegrams.put(Telegram(destination_address=GroupAddress(a.group), payload=GroupValueWrite(p)))
            await x.telegrams.join()
            await asyncio.sleep(0.3)
            return done("pass", {"data": hexdata(p)})
        if a.op == "read":
            t = await ValueReader(x, GroupAddress(a.group), timeout_in_seconds=a.timeout).read()
            if t is None:
                return done("fail", error="no response within %gs" % a.timeout)
            data = hexdata(t.payload.value)
            value = None
            tr = DPTBase.parse_transcoder(a.dpt)
            if tr is not None:
                value = tr.from_knx(t.payload.value)
            return done("pass", {"source": str(t.source_address), "data": data, "value": value})
        if a.op == "monitor":
            x.telegram_queue.register_telegram_received_cb(cb)
            contract.ready()
            try:
                await asyncio.wait_for(got.wait(), a.timeout)
            except asyncio.TimeoutError:
                pass
            tel = [{"source": str(t.source_address), "group": str(t.destination_address), "service": service(t.payload),
                    "data": hexdata(getattr(t.payload, "value", None))} for t in received]
            ok = len(tel) >= a.count
            return done("pass" if ok else "fail", {"telegrams": tel}, None if ok else "received %d of %d telegrams" % (len(tel), a.count))
        if a.op == "answer":
            p = payload(a.dpt, a.value)
            answered = 0
            answered_all = asyncio.Event()

            def on_read(t: Telegram):
                nonlocal answered
                if isinstance(t.payload, GroupValueRead) and str(t.destination_address) == a.group:
                    x.telegrams.put_nowait(Telegram(destination_address=GroupAddress(a.group), payload=GroupValueResponse(p)))
                    answered += 1
                    if answered >= a.count:
                        answered_all.set()

            x.telegram_queue.register_telegram_received_cb(on_read)
            contract.ready()
            try:
                await asyncio.wait_for(answered_all.wait(), a.timeout)
            except asyncio.TimeoutError:
                pass
            await x.telegrams.join()
            await asyncio.sleep(0.3)
            return done("pass", {"answered": answered})
    finally:
        await x.stop()


def main():
    a = contract.parser().parse_args()
    if getattr(a, "target", ""):
        # xknx wants IPv4 addresses, not host names.
        a.target = socket.gethostbyname(a.target)
    if a.role == "capabilities":
        contract.capabilities(IMPL, VERSION, ["client"],
                              {"discover": True, "describe": True, "tunnel": True, "routing": True, "nat": True,
                               "answer": True, "secure": False, "tcp": True, "property": False, "busmonitor": False},
                              "xknx supports KNX IP Secure and Data Secure; this adapter does not exercise them yet")
        return
    if a.role == "server":
        r = contract.Result(IMPL, VERSION, "server")
        r.finish("unsupported", error="xknx has no KNXnet/IP server")
    r = contract.Result(IMPL, VERSION, a.op)
    if a.op in ("property", "busmonitor"):
        r.finish("unsupported", error="the adapter does not drive xknx's device management or busmonitor")
    try:
        res = asyncio.run(run(a))
        if res is None:
            r.finish("fail", error="no result")
        r.finish(*res)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        r.finish("fail", error=repr(e))


if __name__ == "__main__":
    main()
