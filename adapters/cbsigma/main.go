// SPDX-License-Identifier: MIT

// Command run is the knx-interop adapter of cB-Sigma knx (Apache-2.0), an
// independent KNXnet/IP client and router in Go, and of its simulator
// knx-sim (docs/CONTAINER_CONTRACT.md):
//
//	run capabilities
//	run client OP [--target H] [--port P] [--nat] [--routing] [--tcp]
//	              [--secure] [--user N] [--group G] [--dpt D] [--value V]
//	              [--data HEX] [--count N] [--timeout SECONDS] [--file F]
//	              [--password P]
//	run sim [--secure] [--session-timeout S] [--routing] [--busy-above N]
//	run sim-ctl CMD [ARG...]
//	run sim-keyring
//
// The contract role is the client: knx-sim does not pass one tunnel's
// group writes to the other tunnels, which the matrix's server scenarios
// rely on, so it is no contract server. "sim" runs knx-sim's gateway (and
// with --routing a KNX IP router built on the knx module) for the
// runner's sim suite; "sim-ctl" drives its fault switches (sim.go).
//
// Each client operation prints one result document as the last line of
// stdout and exits 0 (pass), 1 (fail) or 3 (unsupported); a usage error
// exits 2.
package main

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net"
	"os"
	"os/signal"
	"runtime/debug"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/cB-Sigma/knx"
)

const (
	impl       = "cB-Sigma knx"
	module     = "github.com/cB-Sigma/knx"
	simModule  = "github.com/cB-Sigma/knx-sim"
	secureDir  = "/adapter/common/secure"
	ifaceName  = "eth0"
	schemaVers = "1.0"
	// routingSource is the individual address of this adapter's routing
	// frames: a Data Secure sender of the test profile (1.1.10 to 1.1.17
	// are the server's tunnelling addresses; routing scenarios have no
	// tunnels on the server's last one).
	routingSource = "1.1.17"
)

// Set by the build (-ldflags -X).
var (
	upstreamRevision = ""
	simRevision      = ""
)

// modVersion is the version of a module in the binary.
func modVersion(path string) string {
	if bi, ok := debug.ReadBuildInfo(); ok {
		for _, d := range bi.Deps {
			if d.Path == path {
				return d.Version
			}
		}
	}
	return "unknown"
}

func version() string { return modVersion(module) }

func main() {
	if len(os.Args) < 2 {
		usage()
	}
	switch os.Args[1] {
	case "capabilities":
		b, _ := json.Marshal(capabilitiesDoc())
		fmt.Println(string(b))
	case "client":
		if len(os.Args) < 3 {
			usage()
		}
		os.Exit(runClient(os.Args[2], os.Args[3:]))
	case "server":
		fmt.Fprintln(os.Stderr, "cbsigma has no contract server: knx-sim does not pass group writes between tunnels; use \"sim\"")
		os.Exit(3)
	case "sim":
		os.Exit(runSim(os.Args[2:]))
	case "sim-ctl":
		os.Exit(runSimCtl(os.Args[2:]))
	case "sim-keyring":
		os.Exit(runSimKeyring())
	default:
		usage()
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, "usage: run capabilities | client OP ... | sim ... | sim-ctl CMD ...")
	os.Exit(2)
}

func capabilitiesDoc() map[string]any {
	return map[string]any{
		"schemaVersion":  schemaVers,
		"implementation": "cbsigma",
		"version":        version(),
		"roles":          []string{"client"},
		"features": map[string]any{
			"discover": true, "describe": true, "tunnel": true, "routing": true, "nat": true, "answer": true,
			"tcp": true, "property": false, "busmonitor": true,
			"secure": true, "dataSecure": true, "secureUdp": false, "surrogate": false,
			"remoteProperty": false, "toolAccess": false, "keyring": true,
		},
		"upstream": map[string]any{
			"name": impl, "version": version(), "revision": upstreamRevision, "independentEngine": true,
		},
		"simulator": map[string]any{
			"name": "cB-Sigma knx-sim", "version": modVersion(simModule), "revision": simRevision,
		},
		"notes": "cB-Sigma knx (Apache-2.0): KNX IP Secure over TCP only; no cEMI device management (M_PropRead) and no " +
			"connection-oriented management. describe is the DESCRIPTION_REQUEST of DialTunnel (the module has no " +
			"stand-alone one). The image also carries knx-sim (sim, sim-ctl), not a contract server.",
	}
}

// args are the contract's options.
type args struct {
	target, group, dptID, value, data string
	port, count, user                 int
	timeout                           float64
	nat, routing, tcp, secure, udp    bool
	file, password                    string
	connected, toolAccess             bool
	object, pid, start                int
	device                            string
}

func parse(fs *flag.FlagSet, a *args, argv []string) error {
	fs.StringVar(&a.target, "target", "", "")
	fs.IntVar(&a.port, "port", 3671, "")
	fs.BoolVar(&a.nat, "nat", false, "")
	fs.BoolVar(&a.routing, "routing", false, "")
	fs.BoolVar(&a.tcp, "tcp", false, "")
	fs.BoolVar(&a.secure, "secure", false, "")
	fs.IntVar(&a.user, "user", 2, "")
	fs.BoolVar(&a.udp, "udp", false, "")
	fs.StringVar(&a.group, "group", "", "")
	fs.StringVar(&a.dptID, "dpt", "", "")
	fs.StringVar(&a.value, "value", "", "")
	fs.StringVar(&a.data, "data", "", "")
	fs.IntVar(&a.count, "count", 1, "")
	fs.Float64Var(&a.timeout, "timeout", 5, "")
	fs.StringVar(&a.file, "file", "", "")
	fs.StringVar(&a.password, "password", "", "")
	fs.IntVar(&a.object, "object", 0, "")
	fs.IntVar(&a.pid, "pid", 11, "")
	fs.IntVar(&a.start, "start", 1, "")
	fs.StringVar(&a.device, "device", "", "")
	fs.BoolVar(&a.connected, "connected", false, "")
	fs.BoolVar(&a.toolAccess, "tool-access", false, "")
	return fs.Parse(argv)
}

func (a *args) wait() time.Duration { return time.Duration(a.timeout * float64(time.Second)) }

func (a *args) endpoint() string { return net.JoinHostPort(a.target, fmt.Sprint(a.port)) }

// profile is the knx-interop KNX Secure test profile (public test values).
type profile struct {
	KeyringFile     string `json:"keyring"`
	KeyringPassword string `json:"keyringPassword"`
	Host            string `json:"host"`
	DevicePassword  string `json:"devicePassword"`
	Users           map[string]struct {
		Password string `json:"password"`
		Address  string `json:"address"`
	} `json:"users"`
	Senders []string `json:"senders"`
	kr      *knx.Keyring
}

func loadProfile() (*profile, error) {
	b, err := os.ReadFile(secureDir + "/profile.json")
	if err != nil {
		return nil, err
	}
	var p profile
	if err := json.Unmarshal(b, &p); err != nil {
		return nil, err
	}
	kb, err := os.ReadFile(secureDir + "/" + p.KeyringFile)
	if err != nil {
		return nil, err
	}
	if p.kr, err = knx.ParseKeyring(kb, p.KeyringPassword); err != nil {
		return nil, err
	}
	return &p, nil
}

// secureOptions are the session credentials of a profile user, from the
// keyring (user 1: the host's management password).
func (p *profile) secureOptions(user int) (*knx.SecureOptions, error) {
	var password string
	if user == 1 {
		for _, d := range p.kr.Devices {
			if d.IndividualAddress == p.Host {
				password = d.ManagementPassword
			}
		}
		if password == "" {
			return nil, errors.New("no management password of the host in the keyring")
		}
	} else {
		in, _, err := p.kr.Tunnel("", user)
		if err != nil {
			return nil, err
		}
		password = in.Password
	}
	return &knx.SecureOptions{UserID: byte(user), PasswordHash: knx.UserPasswordHash(password),
		DeviceAuth: knx.DeviceAuthCode(p.DevicePassword)}, nil
}

// --- client ---------------------------------------------------------

var errUnsupported = errors.New("unsupported")

func runClient(op string, argv []string) int {
	start := time.Now()
	var a args
	fs := flag.NewFlagSet(op, flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	err := parse(fs, &a, argv)
	var data map[string]any
	if err == nil {
		var p *profile
		if a.secure {
			p, err = loadProfile()
			if err != nil {
				err = fmt.Errorf("profile: %w", err)
			}
		}
		if err == nil {
			ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
			data, err = do(ctx, op, &a, p)
			stop()
		}
	}
	status := "pass"
	switch {
	case errors.Is(err, errUnsupported):
		status = "unsupported"
	case err != nil:
		status = "fail"
	}
	if data == nil {
		data = map[string]any{}
	}
	doc := map[string]any{"schemaVersion": schemaVers, "implementation": "cbsigma", "version": version(), "op": op,
		"status": status, "durationMs": time.Since(start).Milliseconds(), "data": data}
	if err != nil {
		doc["error"] = err.Error()
	}
	b, _ := json.Marshal(doc)
	fmt.Println(string(b))
	switch status {
	case "pass":
		return 0
	case "unsupported":
		return 3
	}
	return 1
}

func do(ctx context.Context, op string, a *args, p *profile) (map[string]any, error) {
	switch op {
	case "discover":
		return discover(ctx, a)
	case "describe":
		return describe(ctx, a)
	case "connect":
		t, err := a.dial(ctx, p, nil)
		if err != nil {
			return nil, err
		}
		defer t.Close()
		return map[string]any{"channel": t.Channel, "address": t.Address.String()}, nil
	case "write":
		return write(ctx, a, p)
	case "read":
		return read(ctx, a, p)
	case "monitor":
		return monitor(ctx, a, p)
	case "answer":
		return answer(ctx, a, p)
	case "busmonitor":
		return busmonitor(ctx, a, p)
	case "keyring":
		return keyring(a)
	case "property":
		return nil, fmt.Errorf("%w: cB-Sigma knx has no cEMI device management (DEVICE_CONFIGURATION_REQUEST)", errUnsupported)
	case "remote-property":
		return nil, fmt.Errorf("%w: cB-Sigma knx has management frames but no management sessions", errUnsupported)
	}
	return nil, fmt.Errorf("%w: operation %q", errUnsupported, op)
}

func discover(ctx context.Context, a *args) (map[string]any, error) {
	rs, err := knx.Search(ctx, "", a.wait())
	if err != nil {
		return nil, err
	}
	devs := []map[string]string{}
	for _, d := range rs {
		devs = append(devs, map[string]string{"endpoint": hpai(d.Control), "name": d.Device.FriendlyName,
			"address": d.Device.Address.String()})
	}
	return map[string]any{"devices": devs}, nil
}

func hpai(h knx.HPAI) string {
	if u := h.UDPAddr(nil); u != nil {
		return u.String()
	}
	return ""
}

// describe sends the DESCRIPTION_REQUEST that DialTunnel starts with; the
// module has no stand-alone description.
func describe(ctx context.Context, a *args) (map[string]any, error) {
	if a.secure || a.tcp {
		return nil, fmt.Errorf("%w: describe over TCP", errUnsupported)
	}
	t, err := a.dial(ctx, nil, nil)
	if err != nil {
		return nil, err
	}
	defer t.Close()
	if t.Gateway == nil {
		return nil, errors.New("the gateway did not answer the DESCRIPTION_REQUEST")
	}
	services := map[string]int{}
	for _, f := range t.Gateway.Families {
		services[familyName(f.ID)] = int(f.Version)
	}
	return map[string]any{"name": t.Gateway.Device.FriendlyName, "address": t.Gateway.Device.Address.String(), "services": services}, nil
}

func familyName(id byte) string {
	switch id {
	case 0x02:
		return "Core"
	case 0x03:
		return "DeviceManagement"
	case 0x04:
		return "Tunnelling"
	case 0x05:
		return "Routing"
	case 0x06:
		return "RemoteLogging"
	case 0x07:
		return "RemoteConfiguration"
	case 0x08:
		return "ObjectServer"
	case 0x09:
		return "Security"
	}
	return fmt.Sprintf("0x%02X", id)
}

// dial opens a tunnel to the target: UDP (--nat), TCP or a secure session.
func (a *args) dial(ctx context.Context, p *profile, onFrame func(knx.LData)) (*knx.Tunnel, error) {
	if a.udp {
		return nil, fmt.Errorf("%w: KNX IP Secure over UDP", errUnsupported)
	}
	o := knx.TunnelOptions{NAT: a.nat, TCP: a.tcp, OnFrame: onFrame, Timeout: a.wait() + 5*time.Second}
	if a.secure {
		so, err := p.secureOptions(a.user)
		if err != nil {
			return nil, err
		}
		o.Secure = so
		if o.DataSecure, err = p.kr.DataSecure(""); err != nil {
			return nil, err
		}
	}
	dctx, cancel := context.WithTimeout(ctx, a.wait()+10*time.Second)
	defer cancel()
	return knx.DialTunnel(dctx, a.endpoint(), o)
}

// link is the sending side of a group operation: a tunnel or routing.
type link struct {
	send  func(context.Context, knx.LData) error
	close func()
}

func (a *args) link(ctx context.Context, p *profile, onFrame func(knx.LData)) (*link, error) {
	if a.routing {
		src, _ := knx.ParseIndividualAddress(routingSource)
		o := knx.RoutingOptions{Interface: ifaceName, Source: src, OnFrame: onFrame}
		if a.secure {
			o.Secure = &knx.SecureRoutingOptions{BackboneKey: p.kr.BackboneKey, Latency: p.kr.BackboneLatency}
			var err error
			if o.DataSecure, err = p.kr.DataSecure(""); err != nil {
				return nil, err
			}
		}
		r, err := knx.ListenRouting(o)
		if err != nil {
			return nil, err
		}
		return &link{send: r.Send, close: r.Close}, nil
	}
	t, err := a.dial(ctx, p, onFrame)
	if err != nil {
		return nil, err
	}
	return &link{send: t.Send, close: t.Close}, nil
}

// groupValue encodes --value with --dpt (or takes --data without a DPT).
func groupValue(a *args) ([]byte, bool, error) {
	if a.dptID == "" {
		b, err := hex.DecodeString(a.data)
		return b, false, err
	}
	d, err := knx.ParseDPT(a.dptID)
	if err != nil && !errors.Is(err, knx.ErrDPTRaw) {
		return nil, false, err
	}
	if errors.Is(err, knx.ErrDPTRaw) {
		if a.data == "" {
			return nil, false, err
		}
		b, err := hex.DecodeString(a.data)
		return b, false, err
	}
	b, err := d.Encode(a.value)
	return b, d.Short(), err
}

func dataHex(f knx.LData) string {
	if f.IsShort {
		return fmt.Sprintf("%02X", f.Short)
	}
	return strings.ToUpper(hex.EncodeToString(f.Data))
}

func serviceName(apci uint16) string {
	switch apci {
	case knx.GroupValueRead:
		return "read"
	case knx.GroupValueResponse:
		return "response"
	case knx.GroupValueWrite:
		return "write"
	}
	return fmt.Sprintf("0x%03X", apci)
}

// incoming reports an indication from the network (not the confirmation
// of our own frame).
func incoming(f knx.LData) bool { return f.GroupTarget && f.Code == knx.LDataInd }

func write(ctx context.Context, a *args, p *profile) (map[string]any, error) {
	g, err := knx.ParseGroupAddress(a.group)
	if err != nil {
		return nil, err
	}
	v, short, err := groupValue(a)
	if err != nil {
		return nil, err
	}
	l, err := a.link(ctx, p, nil)
	if err != nil {
		return nil, err
	}
	defer l.close()
	sctx, cancel := context.WithTimeout(ctx, a.wait()+5*time.Second)
	defer cancel()
	if err := l.send(sctx, knx.GroupFrame(knx.LDataReq, g, knx.GroupValueWrite, v, short)); err != nil {
		return nil, err
	}
	if a.routing {
		time.Sleep(200 * time.Millisecond) // the datagram leaves before the socket closes
	}
	return map[string]any{"data": dataHex(knx.GroupFrame(knx.LDataReq, g, knx.GroupValueWrite, v, short))}, nil
}

func read(ctx context.Context, a *args, p *profile) (map[string]any, error) {
	g, err := knx.ParseGroupAddress(a.group)
	if err != nil {
		return nil, err
	}
	resp := make(chan knx.LData, 4)
	l, err := a.link(ctx, p, func(f knx.LData) {
		if incoming(f) && f.APCI == knx.GroupValueResponse && f.Group() == g {
			select {
			case resp <- f:
			default:
			}
		}
	})
	if err != nil {
		return nil, err
	}
	defer l.close()
	rctx, cancel := context.WithTimeout(ctx, a.wait())
	defer cancel()
	if err := l.send(rctx, knx.GroupFrame(knx.LDataReq, g, knx.GroupValueRead, nil, false)); err != nil {
		return nil, err
	}
	select {
	case f := <-resp:
		data := map[string]any{"source": f.Source.String(), "data": dataHex(f)}
		if a.dptID != "" {
			if d, err := knx.ParseDPT(a.dptID); err == nil {
				if v, err := d.Decode(f.Value()); err == nil {
					data["value"] = v
				}
			}
		}
		return data, nil
	case <-rctx.Done():
		return nil, fmt.Errorf("no response to the read of %s within %v", g, a.wait())
	}
}

func monitor(ctx context.Context, a *args, p *profile) (map[string]any, error) {
	var mu sync.Mutex
	tel := []map[string]string{}
	done := make(chan struct{})
	l, err := a.link(ctx, p, func(f knx.LData) {
		if !incoming(f) {
			return
		}
		mu.Lock()
		defer mu.Unlock()
		if len(tel) == a.count {
			return
		}
		tel = append(tel, map[string]string{"source": f.Source.String(), "group": f.Group().String(),
			"service": serviceName(f.APCI), "data": dataHex(f)})
		if len(tel) == a.count {
			close(done)
		}
	})
	if err != nil {
		return nil, err
	}
	defer l.close()
	fmt.Fprintln(os.Stderr, "READY")
	select {
	case <-done:
	case <-time.After(a.wait()):
	case <-ctx.Done():
	}
	mu.Lock()
	defer mu.Unlock()
	data := map[string]any{"telegrams": tel}
	if len(tel) < a.count {
		return data, fmt.Errorf("received %d of %d telegrams", len(tel), a.count)
	}
	return data, nil
}

func answer(ctx context.Context, a *args, p *profile) (map[string]any, error) {
	g, err := knx.ParseGroupAddress(a.group)
	if err != nil {
		return nil, err
	}
	v, short, err := groupValue(a)
	if err != nil {
		return nil, err
	}
	reads := make(chan struct{}, 16)
	l, err := a.link(ctx, p, func(f knx.LData) {
		if incoming(f) && f.APCI == knx.GroupValueRead && f.Group() == g {
			select {
			case reads <- struct{}{}:
			default:
			}
		}
	})
	if err != nil {
		return nil, err
	}
	defer l.close()
	fmt.Fprintln(os.Stderr, "READY")
	answered := 0
	deadline := time.After(a.wait())
	for answered < a.count {
		select {
		case <-reads:
			sctx, cancel := context.WithTimeout(ctx, 10*time.Second)
			err := l.send(sctx, knx.GroupFrame(knx.LDataReq, g, knx.GroupValueResponse, v, short))
			cancel()
			if err != nil {
				return map[string]any{"answered": answered}, err
			}
			answered++
		case <-deadline:
			return map[string]any{"answered": answered}, nil
		case <-ctx.Done():
			return map[string]any{"answered": answered}, nil
		}
	}
	time.Sleep(300 * time.Millisecond) // the last answer leaves before the link closes
	return map[string]any{"answered": answered}, nil
}

func busmonitor(ctx context.Context, a *args, p *profile) (map[string]any, error) {
	var mu sync.Mutex
	frames := []map[string]string{}
	done := make(chan struct{})
	o := knx.TunnelOptions{NAT: a.nat, TCP: a.tcp, Layer: knx.LayerBusmonitor, Timeout: a.wait() + 5*time.Second,
		OnBusmon: func(b knx.Busmon) {
			mu.Lock()
			defer mu.Unlock()
			if len(frames) == a.count {
				return
			}
			frames = append(frames, map[string]string{"raw": strings.ToUpper(hex.EncodeToString(b.Raw))})
			if len(frames) == a.count {
				close(done)
			}
		}}
	if a.secure {
		so, err := p.secureOptions(a.user)
		if err != nil {
			return nil, err
		}
		o.Secure = so
	}
	dctx, cancel := context.WithTimeout(ctx, a.wait()+10*time.Second)
	t, err := knx.DialTunnel(dctx, a.endpoint(), o)
	cancel()
	if err != nil {
		return nil, err
	}
	defer t.Close()
	fmt.Fprintln(os.Stderr, "READY")
	select {
	case <-done:
	case <-time.After(a.wait()):
	case <-ctx.Done():
	}
	mu.Lock()
	defer mu.Unlock()
	data := map[string]any{"frames": frames}
	if len(frames) < a.count {
		return data, fmt.Errorf("received %d of %d frames", len(frames), a.count)
	}
	return data, nil
}
