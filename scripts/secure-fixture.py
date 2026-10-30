#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the KNX Secure test profile of knx-interop (adapters/common/secure,
copied into every adapter image): a keyring, the equivalent Calimero server
keyfile and profile.json. Every key and password is a public test value;
never use them in an installation.

The keyring follows the ETS keyring format (namespace
http://knx.org/xml/keyring/1) as the KNX keyring support article describes
it: values AES-128-CBC encrypted with PBKDF2-HMAC-SHA256("1.keyring.ets.knx.org")
of the password and the IV SHA-256(Created)[:16], passwords prefixed with 8
random octets and padded, and a signature over the document's canonical
form. xknx, Calimero and go-knx read it.

Needs the Python package cryptography (the xknx image has it):
    make fixture
"""

import base64
import hashlib
import json
import os
import sys
from xml.sax.saxutils import quoteattr

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEYRING_PASSWORD = "knx-interop"
DEVICE_PASSWORD = "knx-interop-device"
BACKBONE_HEX = "6b6e782d696e7465726f702d6b657921"  # "knx-interop-key!"
CREATED = "2026-10-30T00:00:00"
HOST = "1.1.0"
USERS = {1: "knx-interop-user1", 2: "knx-interop-user2", 3: "knx-interop-user3"}
USER_ADDRESS = {2: "1.1.10", 3: "1.1.11"}
GROUPS = {"1/3/1": "64732d67726f75702d6b65792d303031", "1/3/2": "64732d67726f75702d6b65792d303032"}
# The Data Secure group Calimero tools write through a surrogate: Calimero
# requires every sender of a group (in all interfaces) to be a device with
# a tool key and picks its surrogate among them, so the group's only
# sender is the surrogate.
SURROGATE_GROUP, SURROGATE_GROUP_KEY = "1/3/3", "64732d67726f75702d6b65792d303033"
# Every address an adapter may send secured telegrams from: the tunnelling
# addresses of the servers and the routing sources (15.15.240 Calimero
# tools, 15.15.250 xknx, 15.15.255 a system under test such as go-knx).
SENDERS = ["1.1.10", "1.1.11", "1.1.12", "1.1.13", "1.1.14", "1.1.15", "1.1.16", "1.1.17", "15.15.240", "15.15.250", "15.15.255"]
# Calimero tools' routing source: its interface lists the surrogate group.
CALIMERO_ROUTING = "15.15.240"
# A device with a tool key, the only sender of the surrogate group: the
# surrogate a system under test (go-knx) plays for Calimero tools.
SURROGATE = "15.15.255"
TOOL_KEYS = {HOST: "746f6f6c000000000000000000000000", SURROGATE: "73757272000000000000000000000000", CALIMERO_ROUTING: "63616c00000000000000000000000000"}


def ga_int(s):
    a, b, c = (int(x) for x in s.split("/"))
    return a << 11 | b << 8 | c


def kdf(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("latin-1"), salt, 65536, 16)


class Encrypter:
    def __init__(self, password, created):
        self.key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), b"1.keyring.ets.knx.org", 65536, 16)
        self.iv = hashlib.sha256(created.encode("utf-8")).digest()[:16]

    def _enc(self, b):
        e = Cipher(algorithms.AES(self.key), modes.CBC(self.iv)).encryptor()
        return base64.b64encode(e.update(b) + e.finalize()).decode()

    def key_(self, hexkey):
        return self._enc(bytes.fromhex(hexkey))

    def password(self, pw):
        b = os.urandom(8) + pw.encode("utf-8")
        n = 16 - len(b) % 16
        return self._enc(b + bytes([n]) * n)


class Element:
    def __init__(self, name):
        self.name, self.attrs, self.children = name, [], []

    def set(self, k, v):
        self.attrs.append((k, v))
        return self

    def child(self, name):
        c = Element(name)
        self.children.append(c)
        return c

    def canonical(self, out):
        def add(s):
            b = s.encode("utf-8")
            if len(b) > 255:
                raise ValueError("value of %d octets in the signature" % len(b))
            out.append(len(b))
            out.extend(b)
        out.append(1)
        add(self.name)
        for k, v in sorted(self.attrs):
            if k not in ("xmlns", "Signature"):
                add(k)
                add(v)
        for c in self.children:
            c.canonical(out)
        out.append(2)

    def write(self, depth=0):
        ind = "  " * depth
        s = ind + "<" + self.name + "".join(" %s=%s" % (k, quoteattr(v)) for k, v in self.attrs)
        if not self.children:
            return s + " />\n"
        return s + ">\n" + "".join(c.write(depth + 1) for c in self.children) + ind + "</" + self.name + ">\n"


def keyring():
    e = Encrypter(KEYRING_PASSWORD, CREATED)
    root = Element("Keyring").set("Project", "knx-interop").set("CreatedBy", "knx-interop secure-fixture").set("Created", CREATED)
    root.child("Backbone").set("MulticastAddress", "224.0.23.12").set("Latency", "1000").set("Key", e.key_(BACKBONE_HEX))
    for uid in (2, 3):
        itf = root.child("Interface").set("IndividualAddress", USER_ADDRESS[uid]).set("Type", "Tunneling").set("Host", HOST) \
            .set("UserID", str(uid)).set("Password", e.password(USERS[uid])).set("Authentication", e.password(DEVICE_PASSWORD))
        for g in sorted(GROUPS, key=ga_int):
            itf.child("Group").set("Address", str(ga_int(g))).set("Senders", " ".join(SENDERS))
    cal = root.child("Interface").set("IndividualAddress", CALIMERO_ROUTING).set("Type", "USB")
    cal.child("Group").set("Address", str(ga_int(SURROGATE_GROUP))).set("Senders", SURROGATE)
    gas = root.child("GroupAddresses")
    for g, k in sorted(list(GROUPS.items()) + [(SURROGATE_GROUP, SURROGATE_GROUP_KEY)], key=lambda x: ga_int(x[0])):
        gas.child("Group").set("Address", str(ga_int(g))).set("Key", e.key_(k))
    devs = root.child("Devices")
    devs.child("Device").set("IndividualAddress", HOST).set("ToolKey", e.key_(TOOL_KEYS[HOST])) \
        .set("ManagementPassword", e.password(USERS[1])).set("Authentication", e.password(DEVICE_PASSWORD))
    devs.child("Device").set("IndividualAddress", SURROGATE).set("ToolKey", e.key_(TOOL_KEYS[SURROGATE]))
    devs.child("Device").set("IndividualAddress", CALIMERO_ROUTING).set("ToolKey", e.key_(TOOL_KEYS[CALIMERO_ROUTING]))
    canon = bytearray()
    root.canonical(canon)
    b64hash = base64.b64encode(e.key).decode()
    canon.append(len(b64hash))
    canon.extend(b64hash.encode())
    root.set("Signature", base64.b64encode(hashlib.sha256(canon).digest()[:16]).decode())
    root.set("xmlns", "http://knx.org/xml/keyring/1")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + root.write()


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: secure-fixture.py <dir>")
    d = sys.argv[1]
    with open(os.path.join(d, "knx-interop.knxkeys"), "w") as f:
        f.write(keyring())
    dev = kdf(DEVICE_PASSWORD, b"device-authentication-code.1.secure.ip.knx.org")
    with open(os.path.join(d, "calimero.keyfile"), "w") as f:
        f.write("# knx-interop KNX Secure test profile (public test values)\n")
        f.write("device.key=%s\ngroup.key=%s\n" % (dev.hex(), BACKBONE_HEX))
        for uid in (1, 2, 3):
            f.write("user[%d].pwd=%s\n" % (uid, USERS[uid]))
    profile = {
        "note": "Public test values of the knx-interop KNX Secure profile. Never use them in an installation.",
        "keyring": "knx-interop.knxkeys",
        "keyringPassword": KEYRING_PASSWORD,
        "host": HOST,
        "devicePassword": DEVICE_PASSWORD,
        "deviceCode": dev.hex(),
        "backboneKey": BACKBONE_HEX,
        "latencyMs": 1000,
        "users": {
            "1": {"password": USERS[1], "role": "management"},
            "2": {"password": USERS[2], "address": USER_ADDRESS[2]},
            "3": {"password": USERS[3], "address": USER_ADDRESS[3]},
        },
        "dataSecureGroups": GROUPS,
        "surrogateGroup": {SURROGATE_GROUP: SURROGATE_GROUP_KEY},
        "senders": SENDERS,
        "surrogate": SURROGATE,
    }
    with open(os.path.join(d, "profile.json"), "w") as f:
        json.dump(profile, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
