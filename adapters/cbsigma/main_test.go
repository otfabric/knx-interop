// SPDX-License-Identifier: MIT

package main

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/cB-Sigma/knx"
)

// testProfileDir is the KNX Secure test profile (public test values):
// adapters/common/secure in the repository; the image build copies it to
// the same place relative to its source directory.
const testProfileDir = "../common/secure"

func parseArgs(t *testing.T, argv ...string) (args, error) {
	t.Helper()
	var a args
	fs := flag.NewFlagSet("test", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	return a, parse(fs, &a, argv)
}

func TestParseDefaults(t *testing.T) {
	a, err := parseArgs(t)
	if err != nil {
		t.Fatal(err)
	}
	want := args{port: 3671, count: 1, user: 2, timeout: 5, pid: 11, start: 1}
	if a != want {
		t.Fatalf("parse() = %+v, want %+v", a, want)
	}
	if a.wait() != 5*time.Second {
		t.Fatalf("wait() = %v, want 5s", a.wait())
	}
}

func TestParseOptions(t *testing.T) {
	a, err := parseArgs(t, "--target", "192.0.2.7", "--port", "3672", "--nat", "--routing", "--tcp", "--secure",
		"--user", "3", "--udp", "--group", "1/0/2", "--dpt", "9.001", "--value", "21.5", "--data", "0C33",
		"--count", "4", "--timeout", "1.5", "--file", "k.knxkeys", "--password", "pw", "--object", "11",
		"--pid", "76", "--start", "2", "--device", "1.1.0", "--connected", "--tool-access")
	if err != nil {
		t.Fatal(err)
	}
	want := args{target: "192.0.2.7", group: "1/0/2", dptID: "9.001", value: "21.5", data: "0C33",
		port: 3672, count: 4, user: 3, timeout: 1.5, nat: true, routing: true, tcp: true, secure: true, udp: true,
		file: "k.knxkeys", password: "pw", connected: true, toolAccess: true, object: 11, pid: 76, start: 2, device: "1.1.0"}
	if a != want {
		t.Fatalf("parse() = %+v, want %+v", a, want)
	}
	if a.wait() != 1500*time.Millisecond {
		t.Fatalf("wait() = %v, want 1.5s", a.wait())
	}
	if a.endpoint() != "192.0.2.7:3672" {
		t.Fatalf("endpoint() = %q", a.endpoint())
	}
}

func TestParseErrors(t *testing.T) {
	for _, argv := range [][]string{
		{"--bogus"},
		{"--port", "x"},
		{"--count", "1.5"},
		{"--timeout", "soon"},
		{"--nat=maybe"},
		{"--group"},
	} {
		if _, err := parseArgs(t, argv...); err == nil {
			t.Errorf("parse(%q): no error", argv)
		}
	}
}

func TestGroupValue(t *testing.T) {
	for _, c := range []struct {
		dpt, value, data string
		want             string
		short            bool
	}{
		// The vectors of fixtures/dpt-vectors.json.
		{dpt: "1.001", value: "on", want: "01", short: true},
		{dpt: "1.001", value: "off", want: "00", short: true},
		{dpt: "5.001", value: "100", want: "FF"},
		{dpt: "5.010", value: "200", want: "C8"},
		{dpt: "7.001", value: "4660", want: "1234"},
		{dpt: "9.001", value: "21.5", want: "0C33"},
		{dpt: "9.001", value: "-30", want: "8A24"},
		{dpt: "9.004", value: "1200", want: "3753"},
		{dpt: "12.001", value: "305419896", want: "12345678"},
		{dpt: "13.001", value: "-2", want: "FFFFFFFE"},
		{dpt: "14.056", value: "1234.5", want: "449A5000"},
		{dpt: "16.000", value: "KNX interop", want: "4B4E5820696E7465726F70000000"},
		// Without a DPT, --data is the value.
		{data: "0C33", want: "0C33"},
		{data: "", want: ""},
		// A DPT the module sends raw takes --data.
		{dpt: "15.000", data: "0102", want: "0102"},
	} {
		a := args{dptID: c.dpt, value: c.value, data: c.data}
		b, short, err := groupValue(&a)
		if err != nil {
			t.Errorf("groupValue(dpt %q, value %q, data %q): %v", c.dpt, c.value, c.data, err)
			continue
		}
		if got := strings.ToUpper(hex.EncodeToString(b)); got != c.want || short != c.short {
			t.Errorf("groupValue(dpt %q, value %q, data %q) = %s, short %v; want %s, short %v",
				c.dpt, c.value, c.data, got, short, c.want, c.short)
		}
	}
}

func TestGroupValueErrors(t *testing.T) {
	for _, c := range []struct {
		dpt, value, data string
		raw              bool
	}{
		{data: "0G"},                   // not hex
		{data: "123"},                  // odd length
		{dpt: "x.001", value: "1"},     // not a DPT
		{dpt: "1.001", value: "maybe"}, // not a value of the DPT
		{dpt: "5.001", value: "fifty"}, // not a number
		{dpt: "15.000", raw: true},     // raw DPT without --data
		{dpt: "15.000", data: "XY"},    // raw DPT, --data not hex
	} {
		a := args{dptID: c.dpt, value: c.value, data: c.data}
		_, _, err := groupValue(&a)
		if err == nil {
			t.Errorf("groupValue(dpt %q, value %q, data %q): no error", c.dpt, c.value, c.data)
			continue
		}
		if c.raw && !errors.Is(err, knx.ErrDPTRaw) {
			t.Errorf("groupValue(dpt %q) = %v, want ErrDPTRaw", c.dpt, err)
		}
	}
}

// testProfile reads the test profile as loadProfile does, from testProfileDir.
func testProfile(t *testing.T) *profile {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(testProfileDir, "profile.json"))
	if err != nil {
		t.Fatal(err)
	}
	var p profile
	if err := json.Unmarshal(b, &p); err != nil {
		t.Fatal(err)
	}
	kb, err := os.ReadFile(filepath.Join(testProfileDir, p.KeyringFile))
	if err != nil {
		t.Fatal(err)
	}
	if p.kr, err = knx.ParseKeyring(kb, p.KeyringPassword); err != nil {
		t.Fatal(err)
	}
	return &p
}

func TestSecureOptions(t *testing.T) {
	p := testProfile(t)
	for _, user := range []int{1, 2, 3} {
		u, ok := p.Users[string(rune('0'+user))]
		if !ok {
			t.Fatalf("the profile has no user %d", user)
		}
		so, err := p.secureOptions(user)
		if err != nil {
			t.Fatalf("secureOptions(%d): %v", user, err)
		}
		if so.UserID != byte(user) {
			t.Errorf("secureOptions(%d).UserID = %d", user, so.UserID)
		}
		// The keyring holds the password the profile names (user 1: the
		// host's management password).
		if !bytes.Equal(so.PasswordHash, knx.UserPasswordHash(u.Password)) {
			t.Errorf("secureOptions(%d).PasswordHash is not that of the profile's password", user)
		}
		if !bytes.Equal(so.DeviceAuth, knx.DeviceAuthCode(p.DevicePassword)) {
			t.Errorf("secureOptions(%d).DeviceAuth is not that of the device password", user)
		}
	}
}

func TestSecureOptionsErrors(t *testing.T) {
	p := testProfile(t)
	if _, err := p.secureOptions(4); err == nil {
		t.Error("secureOptions(4): no error for a user the keyring does not have")
	}
	p.Host = "15.15.1"
	if _, err := p.secureOptions(1); err == nil {
		t.Error("secureOptions(1): no error without the host's management password")
	}
}
