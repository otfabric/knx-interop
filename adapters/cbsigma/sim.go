// SPDX-License-Identifier: MIT

package main

// "sim" runs cB-Sigma knx-sim's simulated gateway on the container's
// address (UDP and TCP port 3671, with --secure a KNX IP Secure gateway
// with the test profile's users and Data Secure groups) and, with
// --routing, a KNX IP router built on the knx module that records what it
// receives. "sim-ctl" drives both through a Unix socket in the container
// (docker exec): fault switches, injected frames, flow control frames and
// what the simulator saw. None of this is part of the container contract:
// the runner's sim suite uses it (scripts/run-matrix.py).

import (
	"bufio"
	"context"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/cB-Sigma/knx"
	"github.com/cB-Sigma/knx-sim/sim"
)

const ctlSocket = "/tmp/knx-sim.sock"

// simTunnelAddresses are knx-sim's tunnelling addresses (1.1.241 to
// 1.1.244): with Data Secure they must be senders of the secured groups.
var simTunnelAddresses = []string{"1.1.241", "1.1.242", "1.1.243", "1.1.244"}

// simObjects are the gateway's group objects: the contract's virtual
// device (1/0/1 to 1/0/5) and the profile's Data Secure groups.
var simObjects = []struct {
	group, data string
	short       bool
}{
	{"1/0/1", "00", true}, {"1/0/2", "0C33", false}, {"1/0/3", "80", false},
	{"1/0/4", "449A5000", false}, {"1/0/5", "696E7465726F7000000000000000", false},
	{"1/3/1", "0C33", false}, {"1/3/2", "0C33", false},
}

type routed struct {
	At      int64  `json:"t"` // Unix milliseconds
	Source  string `json:"source"`
	Group   string `json:"group"`
	Service string `json:"service"`
	Data    string `json:"data"`
}

type simState struct {
	gw     *sim.Server
	router *knx.Router
	// raw sends the test's own routing indications past the router's flow
	// control: the router sees its own ROUTING_BUSY on the multicast
	// loopback and would hold them back too.
	raw    *net.UDPConn
	mu     sync.Mutex
	frames []routed
	busy   int
	lost   int
}

func localIP() (string, error) {
	itf, err := net.InterfaceByName(ifaceName)
	if err != nil {
		return "", err
	}
	addrs, err := itf.Addrs()
	if err != nil {
		return "", err
	}
	for _, a := range addrs {
		if n, ok := a.(*net.IPNet); ok && n.IP.To4() != nil {
			return n.IP.String(), nil
		}
	}
	return "", fmt.Errorf("no IPv4 address on %s", ifaceName)
}

func runSim(argv []string) int {
	fs := flag.NewFlagSet("sim", flag.ContinueOnError)
	secure := fs.Bool("secure", false, "KNX IP Secure gateway (test profile) with Data Secure")
	timeout := fs.Float64("session-timeout", 60, "secure session timeout in seconds")
	routing := fs.Bool("routing", false, "run a KNX IP router on 224.0.23.12:3671 instead of the gateway (both need port 3671)")
	_ = fs.String("name", "", "ignored: knx-sim's friendly name is fixed")
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	ip, err := localIP()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	o := sim.Options{Listen: ip + ":3671", ListenTCP: ip + ":3671", TCP: true}
	if *secure {
		p, err := loadProfile()
		if err != nil {
			fmt.Fprintln(os.Stderr, "profile:", err)
			return 1
		}
		users := map[byte]string{}
		for id, u := range p.Users {
			n, err := strconv.Atoi(id)
			if err != nil || n < 1 || n > 127 {
				fmt.Fprintln(os.Stderr, "profile: user", id)
				return 1
			}
			users[byte(n)] = u.Password
		}
		o.Secure = &sim.SecureConfig{Users: users, DeviceAuth: p.DevicePassword,
			SessionTimeout: time.Duration(*timeout * float64(time.Second))}
		senders := map[knx.IndividualAddress]uint64{}
		for _, s := range append(append([]string(nil), p.Senders...), simTunnelAddresses...) {
			ia, err := knx.ParseIndividualAddress(s)
			if err != nil {
				fmt.Fprintln(os.Stderr, "profile: sender", s)
				return 1
			}
			senders[ia] = 0
		}
		if o.DataSecure, err = knx.NewDataSecure(knx.DataSecureOptions{GroupKeys: p.kr.DataSecureKeys, Senders: senders}); err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
	}
	st := &simState{}
	if !*routing {
		if st.gw, err = sim.StartWith(o); err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		defer st.gw.Close()
		for _, obj := range simObjects {
			g, _ := knx.ParseGroupAddress(obj.group)
			b, _ := hex.DecodeString(obj.data)
			if obj.short {
				st.gw.SetShort(g, b[0])
			} else {
				st.gw.Set(g, b)
			}
		}
	}
	if *routing {
		src, _ := knx.ParseIndividualAddress("1.1.16")
		st.router, err = knx.ListenRouting(knx.RoutingOptions{Interface: ifaceName, Source: src, MinInterval: -1,
			OnFrame: st.onRouted,
			OnBusy:  func(knx.RoutingBusy) { st.mu.Lock(); st.busy++; st.mu.Unlock() },
			OnLostMessage: func(knx.RoutingLostMessage) {
				st.mu.Lock()
				st.lost++
				st.mu.Unlock()
			}})
		if err != nil {
			fmt.Fprintln(os.Stderr, "routing:", err)
			return 1
		}
		defer st.router.Close()
		group, err := net.ResolveUDPAddr("udp4", knx.DefaultMulticast)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		if st.raw, err = net.DialUDP("udp4", nil, group); err != nil {
			fmt.Fprintln(os.Stderr, "routing:", err)
			return 1
		}
		defer st.raw.Close()
	}
	_ = os.Remove(ctlSocket)
	ln, err := net.Listen("unix", ctlSocket)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	defer ln.Close()
	go st.serveCtl(ln)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	fmt.Fprintln(os.Stderr, "READY")
	<-ctx.Done()
	return 0
}

func (st *simState) onRouted(f knx.LData) {
	if !f.GroupTarget {
		return
	}
	st.mu.Lock()
	defer st.mu.Unlock()
	st.frames = append(st.frames, routed{At: time.Now().UnixMilli(), Source: f.Source.String(), Group: f.Group().String(),
		Service: serviceName(f.APCI), Data: dataHex(f)})
}

func (st *simState) serveCtl(ln net.Listener) {
	for {
		c, err := ln.Accept()
		if err != nil {
			return
		}
		go func() {
			defer c.Close()
			var cmd []string
			if err := json.NewDecoder(bufio.NewReader(c)).Decode(&cmd); err != nil || len(cmd) == 0 {
				_ = json.NewEncoder(c).Encode(map[string]any{"error": "want a JSON array: command and arguments"})
				return
			}
			out, err := st.ctl(cmd[0], cmd[1:])
			if err != nil {
				out = map[string]any{"error": err.Error()}
			}
			_ = json.NewEncoder(c).Encode(out)
		}()
	}
}

func groupAndData(args []string) (knx.GroupAddress, []byte, bool, error) {
	if len(args) < 2 {
		return 0, nil, false, errors.New("want GROUP HEX [short]")
	}
	g, err := knx.ParseGroupAddress(args[0])
	if err != nil {
		return 0, nil, false, err
	}
	b, err := hex.DecodeString(args[1])
	if err != nil || len(b) == 0 {
		return 0, nil, false, fmt.Errorf("data %q", args[1])
	}
	return g, b, len(args) > 2 && args[2] == "short", nil
}

func onOff(args []string) (bool, error) {
	if len(args) != 1 || (args[0] != "on" && args[0] != "off") {
		return false, errors.New("want on or off")
	}
	return args[0] == "on", nil
}

// ctl runs one control command; every answer carries the simulator's
// clock ("now", Unix milliseconds).
func (st *simState) ctl(cmd string, args []string) (map[string]any, error) {
	out := map[string]any{}
	needGateway := func() error {
		if st.gw == nil {
			return errors.New("the simulator runs a router (--routing), not a gateway")
		}
		return nil
	}
	needRouter := func() error {
		if st.router == nil {
			return errors.New("the simulator runs without --routing")
		}
		return nil
	}
	switch cmd {
	case "stats":
		st.mu.Lock()
		out["routed"] = append([]routed(nil), st.frames...)
		out["busyReceived"], out["lostReceived"] = st.busy, st.lost
		st.mu.Unlock()
		if st.gw == nil {
			break
		}
		var writes []map[string]string
		for _, w := range st.gw.Writes() {
			writes = append(writes, map[string]string{"group": w.GA.String(), "data": fmt.Sprintf("%X", w.Data)})
		}
		var reads []string
		for _, g := range st.gw.Reads() {
			reads = append(reads, g.String())
		}
		for k, v := range map[string]any{"connects": st.gw.Connects(), "channels": st.gw.Channels(), "sessions": st.gw.Sessions(),
			"keepalives": st.gw.Keepalives(), "rejected": st.gw.Rejected(), "tcpAcks": st.gw.TCPAcks(),
			"dataSecureRefused": st.gw.DataSecureRefused(), "writes": writes, "reads": reads} {
			out[k] = v
		}
	case "inject", "inject-duplicate", "inject-tampered":
		if err := needGateway(); err != nil {
			return nil, err
		}
		g, b, short, err := groupAndData(args)
		if err != nil {
			return nil, err
		}
		switch cmd {
		case "inject":
			st.gw.Inject(g, b, short)
		case "inject-duplicate":
			st.gw.InjectDuplicate(g, b, short)
		default:
			st.gw.InjectTampered(g, b, short)
		}
	case "replay":
		if err := needGateway(); err != nil {
			return nil, err
		}
		st.gw.ReplayLast()
	case "end-sessions":
		if err := needGateway(); err != nil {
			return nil, err
		}
		if len(args) != 1 {
			return nil, errors.New("want STATUS")
		}
		n, err := strconv.ParseUint(args[0], 0, 8)
		if err != nil {
			return nil, err
		}
		st.gw.EndSessions(byte(n))
	case "silent":
		if err := needGateway(); err != nil {
			return nil, err
		}
		v, err := onOff(args)
		if err != nil {
			return nil, err
		}
		st.gw.SetSilent(v)
	case "drop-acks":
		if err := needGateway(); err != nil {
			return nil, err
		}
		v, err := onOff(args)
		if err != nil {
			return nil, err
		}
		st.gw.DropAcks(v)
	case "drop-streams":
		if err := needGateway(); err != nil {
			return nil, err
		}
		st.gw.DropStreams()
	case "route-read", "busy-read":
		// busy-read MS GROUP: a ROUTING_BUSY with wait time MS, then at
		// once a GroupValue_Read whose answer flow control must hold back.
		if err := needRouter(); err != nil {
			return nil, err
		}
		if cmd == "busy-read" {
			if len(args) != 2 {
				return nil, errors.New("want MS GROUP")
			}
			ms, err := strconv.Atoi(args[0])
			if err != nil || ms < 0 || ms > 65535 {
				return nil, fmt.Errorf("wait time %q", args[0])
			}
			out["busyAt"] = time.Now().UnixMilli()
			if err := st.router.SendBusy(time.Duration(ms) * time.Millisecond); err != nil {
				return nil, err
			}
			args = args[1:]
		}
		if len(args) != 1 {
			return nil, errors.New("want GROUP")
		}
		g, err := knx.ParseGroupAddress(args[0])
		if err != nil {
			return nil, err
		}
		f := knx.GroupFrame(knx.LDataInd, g, knx.GroupValueRead, nil, false)
		f.Source = 0x1110 // 1.1.16
		out["readAt"] = time.Now().UnixMilli()
		if _, err := st.raw.Write(knx.RoutingIndication(f.Encode()).Encode()); err != nil {
			return nil, err
		}
	case "lost":
		if err := needRouter(); err != nil {
			return nil, err
		}
		if len(args) != 1 {
			return nil, errors.New("want N")
		}
		n, err := strconv.ParseUint(args[0], 0, 16)
		if err != nil {
			return nil, err
		}
		out["lostAt"] = time.Now().UnixMilli()
		if err := st.router.SendLostMessage(uint16(n)); err != nil {
			return nil, err
		}
	default:
		return nil, fmt.Errorf("unknown command %q", cmd)
	}
	out["now"] = time.Now().UnixMilli()
	return out, nil
}

// runSimCtl sends one command to the simulator of this container and
// prints its JSON answer; it exits 1 when the simulator reports an error.
func runSimCtl(argv []string) int {
	if len(argv) == 0 {
		fmt.Fprintln(os.Stderr, "usage: run sim-ctl CMD [ARG...]")
		return 2
	}
	c, err := net.DialTimeout("unix", ctlSocket, 5*time.Second)
	if err != nil {
		fmt.Println(`{"error":"no simulator: ` + err.Error() + `"}`)
		return 1
	}
	defer c.Close()
	_ = c.SetDeadline(time.Now().Add(30 * time.Second))
	if err := json.NewEncoder(c).Encode(argv); err != nil {
		fmt.Println(`{"error":"` + err.Error() + `"}`)
		return 1
	}
	var out map[string]any
	if err := json.NewDecoder(c).Decode(&out); err != nil {
		fmt.Println(`{"error":"` + err.Error() + `"}`)
		return 1
	}
	b, _ := json.Marshal(out)
	fmt.Println(string(b))
	if _, bad := out["error"]; bad {
		return 1
	}
	return 0
}
