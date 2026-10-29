// SPDX-License-Identifier: MIT

// Command secure-fixture writes the KNX Secure test profile of
// knx-interop (adapters/common/secure, copied into every adapter image at /adapter/common/secure): a keyring, the equivalent Calimero server
// keyfile and profile.json. Every key and password in it is a public test
// value; never use them in an installation.
//
//	go run . ../../adapters/common/secure
package main

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/otfabric/go-knx"
	"github.com/otfabric/go-knx/keyring"
	"github.com/otfabric/go-knx/secure"
)

// The profile.
const (
	keyringPassword = "knx-interop"
	devicePassword  = "knx-interop-device"
	backboneHex     = "6b6e782d696e7465726f702d6b657921" // "knx-interop-key!"
)

var (
	host        = knx.MustParseIndividualAddress("1.1.0")
	users       = map[uint8]string{1: "knx-interop-user1", 2: "knx-interop-user2", 3: "knx-interop-user3"}
	userAddress = map[uint8]knx.IndividualAddress{2: knx.MustParseIndividualAddress("1.1.10"), 3: knx.MustParseIndividualAddress("1.1.11")}
	groups      = map[string]string{"1/3/1": "64732d67726f75702d6b65792d303031", "1/3/2": "64732d67726f75702d6b65792d303032"}
	// Every address an adapter may send secured telegrams from: the
	// tunnelling addresses of the servers and the routing sources of the
	// stacks (15.15.250 xknx, 15.15.255 go-knx, 15.15.240 Calimero tools).
	senders = []string{"1.1.10", "1.1.11", "1.1.12", "1.1.13", "1.1.14", "1.1.15", "1.1.16", "1.1.17", "15.15.240", "15.15.250", "15.15.255"}
	// Interfaces of the routing sources, so that keyring readers that look
	// up their own address find the groups.
	routingInterfaces = []string{"15.15.240", "15.15.250", "15.15.255"}
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: secure-fixture <dir>")
		os.Exit(2)
	}
	dir := os.Args[1]
	var backbone keyring.Key
	mustHex(backboneHex, backbone[:])
	gk := map[knx.GroupAddress]keyring.Key{}
	var senderIAs []knx.IndividualAddress
	for _, s := range senders {
		senderIAs = append(senderIAs, knx.MustParseIndividualAddress(s))
	}
	assigned := map[knx.GroupAddress][]knx.IndividualAddress{}
	for g, k := range groups {
		ga := knx.MustParseGroupAddress(g)
		var key keyring.Key
		mustHex(k, key[:])
		gk[ga] = key
		assigned[ga] = senderIAs
	}
	kr := &keyring.Keyring{Project: "knx-interop", CreatedBy: "knx-interop secure-fixture", Created: "2026-10-30T00:00:00",
		Backbone:  &keyring.Backbone{MulticastAddress: "224.0.23.12", Latency: time.Second, Key: backbone},
		GroupKeys: gk,
		Devices: []keyring.Device{{IndividualAddress: host, ToolKey: keyring.Key{0x74, 0x6f, 0x6f, 0x6c}, HasToolKey: true,
			ManagementPassword: users[1], Authentication: devicePassword}},
	}
	for _, id := range []uint8{2, 3} {
		kr.Interfaces = append(kr.Interfaces, keyring.Interface{Type: keyring.Tunneling, IndividualAddress: userAddress[id], Host: host, HasHost: true,
			UserID: id, Password: users[id], Authentication: devicePassword, Groups: assigned})
	}
	for _, a := range routingInterfaces {
		kr.Interfaces = append(kr.Interfaces, keyring.Interface{Type: keyring.USB, IndividualAddress: knx.MustParseIndividualAddress(a), Groups: assigned})
	}
	b, err := kr.Encode(keyringPassword)
	check(err)
	check(os.WriteFile(filepath.Join(dir, "knx-interop.knxkeys"), b, 0o644))

	dev, err := secure.DeviceAuthenticationCode(devicePassword)
	check(err)
	keyfile := fmt.Sprintf("# knx-interop KNX Secure test profile (public test values)\ndevice.key=%x\ngroup.key=%s\n", dev[:], backboneHex)
	for _, id := range []uint8{1, 2, 3} {
		keyfile += fmt.Sprintf("user[%d].pwd=%s\n", id, users[id])
	}
	check(os.WriteFile(filepath.Join(dir, "calimero.keyfile"), []byte(keyfile), 0o644))

	profile := map[string]any{
		"note":            "Public test values of the knx-interop KNX Secure profile. Never use them in an installation.",
		"keyring":         "knx-interop.knxkeys",
		"keyringPassword": keyringPassword,
		"host":            host.String(),
		"devicePassword":  devicePassword,
		"deviceCode":      hex.EncodeToString(dev[:]),
		"backboneKey":     backboneHex,
		"latencyMs":       1000,
		"users": map[string]any{
			"1": map[string]string{"password": users[1], "role": "management"},
			"2": map[string]string{"password": users[2], "address": userAddress[2].String()},
			"3": map[string]string{"password": users[3], "address": userAddress[3].String()},
		},
		"dataSecureGroups": groups,
		"senders":          senders,
	}
	pb, err := json.MarshalIndent(profile, "", "  ")
	check(err)
	check(os.WriteFile(filepath.Join(dir, "profile.json"), append(pb, '\n'), 0o644))
}

func mustHex(s string, dst []byte) {
	b, err := hex.DecodeString(s)
	check(err)
	copy(dst, b)
}

func check(err error) {
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
