#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""knx-interop raw KNXnet/IP probe: hand-built datagrams for readiness checks
and negative tests against any server. It is written from the frame
structures of the KNXnet/IP standard with the Python standard library only and
shares no code with the implementations under test."""

import socket
import struct
import sys
import time

sys.path.insert(0, "/adapter/common")
import contract  # noqa: E402

IMPL = "probe"
VERSION = "1.0"

SEARCH_REQ, SEARCH_RES = 0x0201, 0x0202
DESC_REQ, DESC_RES = 0x0203, 0x0204
CONN_REQ, CONN_RES = 0x0205, 0x0206
CS_REQ, CS_RES = 0x0207, 0x0208
DISC_REQ, DISC_RES = 0x0209, 0x020A
TUN_REQ, TUN_ACK = 0x0420, 0x0421


def frame(service, body, version=0x10, hlen=6, total=None):
    if total is None:
        total = 6 + len(body)
    return struct.pack(">BBHH", hlen, version, service, total) + body


def hpai(ip="0.0.0.0", port=0, proto=1):
    return struct.pack(">BB4sH", 8, proto, socket.inet_aton(ip), port)


def tunnel_cri(layer=0x02, ctype=0x04):
    return bytes([4, ctype, layer, 0])


def ldata_write(group=0x0801, value=1):
    # L_Data.req, no additional info, standard frame, low priority, group
    # destination, hop count 6, source 0.0.0, A_GroupValue_Write small value.
    return bytes([0x11, 0x00, 0xBC, 0xE0, 0x00, 0x00, group >> 8, group & 0xFF, 0x01, 0x00, 0x80 | (value & 0x3F)])


class Peer:
    def __init__(self, target, port):
        self.addr = (socket.gethostbyname(target), port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("0.0.0.0", 0))

    def send(self, data):
        self.s.sendto(data, self.addr)

    def recv(self, want=None, timeout=1.0):
        """Return (service, body) of the next datagram of a wanted service
        within timeout, or None."""
        end = time.monotonic() + timeout
        while True:
            left = end - time.monotonic()
            if left <= 0:
                return None
            self.s.settimeout(left)
            try:
                data, _ = self.s.recvfrom(2048)
            except socket.timeout:
                return None
            if len(data) < 6:
                continue
            svc = struct.unpack(">H", data[2:4])[0]
            if want is None or svc in want:
                return svc, data[6:]

    def alive(self, attempts=3):
        """The server answers a DESCRIPTION_REQUEST within attempts
        seconds (one request per second: servers may throttle them)."""
        for _ in range(attempts):
            self.send(frame(DESC_REQ, hpai()))
            if self.recv({DESC_RES}, 1.0) is not None:
                return True
        return False

    def connect(self, cri=None, ctrl=None):
        self.send(frame(CONN_REQ, (ctrl or hpai()) + hpai() + (cri or tunnel_cri())))
        r = self.recv({CONN_RES}, 3.0)
        if r is None:
            return None, None
        body = r[1]
        return body[0], body[1]

    def disconnect(self, ch):
        self.send(frame(DISC_REQ, bytes([ch, 0]) + hpai()))
        r = self.recv({DISC_RES}, 2.0)
        return None if r is None else r[1][1]

    def state(self, ch):
        self.send(frame(CS_REQ, bytes([ch, 0]) + hpai()))
        r = self.recv({CS_RES}, 2.0)
        return None if r is None else r[1][1]

    def tunnel(self, ch, seq, cemi):
        self.send(frame(TUN_REQ, bytes([4, ch, seq, 0]) + cemi))
        end = time.monotonic() + 1.0
        while time.monotonic() < end:
            r = self.recv({TUN_ACK, TUN_REQ}, end - time.monotonic())
            if r is None:
                return None
            svc, body = r
            if svc == TUN_REQ:
                # Acknowledge the server's L_Data.con and indications.
                self.send(frame(TUN_ACK, bytes([4, body[1], body[2], 0])))
                continue
            if body[1] == ch and body[2] == seq:
                return body[3]
        return None


def negative(a):
    p = Peer(a.target, a.port)
    checks = []

    def check(name, ok, detail, kind="required"):
        checks.append({"name": name, "status": "pass" if ok else ("fail" if kind == "required" else "info"), "detail": detail, "kind": kind})

    if not p.alive():
        return "fail", {"checks": checks}, "the server does not answer DESCRIPTION_REQUEST"
    malformed = [
        ("header length 7", frame(DESC_REQ, hpai(), hlen=7)),
        ("protocol version 0x20", frame(DESC_REQ, hpai(), version=0x20)),
        ("total length longer than the datagram", frame(DESC_REQ, hpai(), total=40)),
        ("total length shorter than the datagram", frame(DESC_REQ, hpai(), total=8)),
        ("truncated header", b"\x06\x10\x02"),
        ("unknown service type 0x0F00", frame(0x0F00, b"\x00" * 8)),
        ("HPAI of length 7", frame(DESC_REQ, hpai()[:-1])),
        ("2000-octet datagram", frame(DESC_REQ, hpai() + b"\x00" * 1986)),
        ("empty CONNECT_REQUEST", frame(CONN_REQ, b"")),
        ("CRI length 0", frame(CONN_REQ, hpai() + hpai() + b"\x00")),
    ]
    for name, data in malformed:
        p.send(data)
        time.sleep(0.05)
        # The server must keep serving: a fresh socket gets a description.
        # A server may stop answering the offending source for a while,
        # which is recorded but allowed.
        fresh = Peer(a.target, a.port)
        ok = fresh.alive()
        if ok:
            same = p.alive(1)
            check("survives " + name, True, "answers DESCRIPTION_REQUEST afterwards" + ("" if same else "; ignores the sender of the malformed datagram for a while"))
            continue
        # No answer within 3 s: wait for the server to come back, so that
        # one outage does not fail the following checks.
        t0 = time.monotonic()
        back = fresh.alive(30)
        check("survives " + name, False, "no DESCRIPTION_RESPONSE for %.0f s%s" % (
            3 + time.monotonic() - t0, ", then the server answered again" if back else " or more"))

    p = Peer(a.target, a.port)
    st = p.state(0xEE)
    check("CONNECTIONSTATE_REQUEST of an unknown channel → E_CONNECTION_ID", st == 0x21, "status %s" % (None if st is None else "0x%02X" % st))
    ch, st = p.connect(cri=bytes([2, 0x07]))
    check("unsupported connection type → E_CONNECTION_TYPE", st == 0x22, "status %s" % (None if st is None else "0x%02X" % st))
    if st == 0:
        p.disconnect(ch)
    ch, st = p.connect(cri=tunnel_cri(layer=0x04))
    check("raw tunnelling layer → refused", st not in (None, 0), "status %s" % (None if st is None else "0x%02X" % st), "observed")
    if st == 0:
        p.disconnect(ch)
    ch, st = p.connect(ctrl=hpai(proto=2))
    check("TCP HPAI over UDP → refused", st not in (None, 0), "status %s" % (None if st is None else "0x%02X" % st), "observed")
    if st == 0:
        p.disconnect(ch)

    # A tunnelling connection: duplicates, order, rollover.
    ch, st = p.connect()
    if st != 0:
        check("tunnelling connection", False, "status %s" % (None if st is None else "0x%02X" % st))
        return finish_checks(checks)
    check("heartbeat on an open channel → E_NO_ERROR", p.state(ch) == 0, "CONNECTIONSTATE_RESPONSE")
    a0 = p.tunnel(ch, 0, ldata_write(value=1))
    check("TUNNELLING_REQUEST sequence 0 acknowledged", a0 == 0, "ack status %r" % a0)
    a0b = p.tunnel(ch, 0, ldata_write(value=1))
    check("repeated sequence 0 acknowledged again (duplicate)", a0b == 0, "ack status %r" % a0b)
    a5 = p.tunnel(ch, 5, ldata_write(value=0))
    check("out-of-order sequence 5 not acknowledged", a5 is None, "ack status %r" % a5)
    ok = True
    seq = 1
    for i in range(1, 260):
        if p.tunnel(ch, seq, ldata_write(value=i & 1)) != 0:
            ok = False
            break
        seq = (seq + 1) & 0xFF
    check("sequence numbers roll over 255 → 0", ok, "259 requests, stopped at %d" % i if not ok else "259 requests acknowledged")
    check("DISCONNECT_REQUEST → E_NO_ERROR", p.disconnect(ch) == 0, "DISCONNECT_RESPONSE")
    st = p.state(ch)
    check("heartbeat after disconnect → E_CONNECTION_ID", st == 0x21, "status %s" % (None if st is None else "0x%02X" % st))

    # Channel exhaustion.
    peers, refused = [], None
    for _ in range(64):
        q = Peer(a.target, a.port)
        ch, st = q.connect()
        if st != 0:
            refused = st
            break
        peers.append((q, ch))
    check("channel exhaustion → E_NO_MORE_CONNECTIONS", refused == 0x24, "%d connections, then status %s" % (len(peers), None if refused is None else "0x%02X" % refused))
    for q, ch in peers:
        q.disconnect(ch)
    check("still serving after the tests", p.alive(), "answers DESCRIPTION_REQUEST")
    return finish_checks(checks)


def finish_checks(checks):
    failed = [c["name"] for c in checks if c["status"] == "fail"]
    return ("fail" if failed else "pass"), {"checks": checks}, ("failed: " + "; ".join(failed)) if failed else None


def main():
    argv = sys.argv[1:]
    if argv[:2] == ["client", "negative"]:
        argv[1] = "describe"
        a = contract.parser().parse_args(argv)
        a.op = "negative"
    else:
        a = contract.parser().parse_args(argv)
    if a.role == "capabilities":
        contract.capabilities(IMPL, VERSION, ["client"], {"describe": True, "negative": True})
        return
    r = contract.Result(IMPL, VERSION, a.op)
    try:
        if a.op == "describe":
            pr = Peer(a.target, a.port)
            if pr.alive():
                r.finish("pass", {})
            r.finish("fail", error="no DESCRIPTION_RESPONSE")
        if a.op == "negative":
            r.finish(*negative(a))
        r.finish("unsupported", error="the probe implements describe and negative only")
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        r.finish("fail", error=repr(e))


if __name__ == "__main__":
    main()
