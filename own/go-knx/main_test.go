// SPDX-License-Identifier: MIT

package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"io"
	"os"
	"strings"
	"testing"
	"time"
)

func TestCapabilitiesSayNotIndependent(t *testing.T) {
	doc := capabilitiesDoc()
	up, ok := doc["upstream"].(map[string]any)
	if !ok {
		t.Fatalf("no upstream object: %v", doc)
	}
	if up["independentEngine"] != false || up["name"] != "go-knx" {
		t.Fatalf("upstream = %v, want go-knx, independentEngine false", up)
	}
	b, err := json.Marshal(doc)
	if err != nil {
		t.Fatal(err)
	}
	var back map[string]any
	if err := json.Unmarshal(b, &back); err != nil {
		t.Fatal(err)
	}
	if back["schemaVersion"] != "1.0" || back["implementation"] != "go-knx" {
		t.Fatalf("capabilities = %s", b)
	}
	roles, _ := back["roles"].([]any)
	if len(roles) != 2 {
		t.Fatalf("roles = %v, want server and client", roles)
	}
}

func TestVersionFromTheBuild(t *testing.T) {
	old := upstreamVersion
	t.Cleanup(func() { upstreamVersion = old })
	upstreamVersion = "v9.9.9"
	if got := version(); got != "v9.9.9" {
		t.Fatalf("version() = %q", got)
	}
}

func TestParseDefaults(t *testing.T) {
	var a args
	if err := parse(flag.NewFlagSet("t", flag.ContinueOnError), &a, []string{"--target", "10.0.0.1", "--timeout", "1.5"}); err != nil {
		t.Fatal(err)
	}
	if a.endpoint() != "10.0.0.1:3671" || a.wait() != 1500*time.Millisecond || a.user != 2 || a.device != serverIA || a.start != 1 {
		t.Fatalf("args = %+v", a)
	}
}

// capture runs fn with stdout redirected and returns what it printed.
func capture(t *testing.T, fn func() int) (string, int) {
	t.Helper()
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	old := os.Stdout
	os.Stdout = w
	code := fn()
	os.Stdout = old
	_ = w.Close()
	var buf bytes.Buffer
	_, _ = io.Copy(&buf, r)
	return strings.TrimSpace(buf.String()), code
}

func TestResultExitCodes(t *testing.T) {
	for _, c := range []struct {
		status string
		err    error
		code   int
	}{{"pass", nil, 0}, {"fail", errors.New("x"), 1}, {"unsupported", errUnsupported, 3}} {
		out, code := capture(t, func() int { return result{op: "read", start: time.Now()}.finish(c.status, nil, c.err) })
		if code != c.code {
			t.Errorf("%s: exit %d, want %d", c.status, code, c.code)
		}
		var doc map[string]any
		if err := json.Unmarshal([]byte(out), &doc); err != nil {
			t.Fatalf("%s: %v: %q", c.status, err, out)
		}
		if doc["status"] != c.status || doc["op"] != "read" || doc["schemaVersion"] != "1.0" {
			t.Errorf("%s: document %v", c.status, doc)
		}
		if _, ok := doc["data"].(map[string]any); !ok {
			t.Errorf("%s: data is not an object: %v", c.status, doc)
		}
	}
}

func TestUnknownOperationIsUnsupported(t *testing.T) {
	out, code := capture(t, func() int { return runClient("negative", nil) })
	if code != 3 || !strings.Contains(out, `"status":"unsupported"`) {
		t.Fatalf("exit %d, %s", code, out)
	}
}

func TestBadOptionFails(t *testing.T) {
	out, code := capture(t, func() int { return runClient("read", []string{"--count", "x"}) })
	if code != 1 || !strings.Contains(out, `"status":"fail"`) {
		t.Fatalf("exit %d, %s", code, out)
	}
}

func TestArgumentRanges(t *testing.T) {
	if _, err := u8Arg("pid", 256); !errors.Is(err, errOption) {
		t.Errorf("u8Arg(256) = %v", err)
	}
	if v, err := u8Arg("pid", 76); err != nil || v != 76 {
		t.Errorf("u8Arg(76) = %d, %v", v, err)
	}
	if _, err := u16Arg("object", -1); !errors.Is(err, errOption) {
		t.Errorf("u16Arg(-1) = %v", err)
	}
}
