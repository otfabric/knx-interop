#!/bin/sh
# SPDX-License-Identifier: MIT
# knx-interop adapter for calimero-tools (GPL-2.0 with the Classpath
# exception): client roles through the Calimero command-line tools.
# Option lists ($(opts), $filt, hex octets) are split on purpose; some
# parsed options are not used by every role.
# shellcheck disable=SC2046,SC2086,SC2034
set -u

IMPL=calimero
TOOLS=/usr/app/calimero-tools/bin/calimero-tools
VERSION=$(cat /adapter/VERSION 2>/dev/null || echo unknown)
START=$(date +%s)

json_str() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n\t' '  '; }

finish() { # status data-json [error]
	now=$(date +%s)
	err=""
	[ $# -ge 3 ] && err=$(printf ',"error":"%s"' "$(json_str "$3")")
	printf '{"data":%s,"durationMs":%d,"implementation":"%s","op":"%s","schemaVersion":"1.0","status":"%s","version":"%s"%s}\n' \
		"$2" $(((now - START) * 1000)) "$IMPL" "$OP" "$1" "$VERSION" "$err"
	case "$1" in pass) exit 0 ;; unsupported) exit 3 ;; *) exit 1 ;; esac
}

ROLE=${1:-}
[ $# -gt 0 ] && shift
OP=$ROLE
if [ "$ROLE" = client ]; then OP=${1:-}; shift; fi
TARGET="" PORT=3671 NAT=0 TCP=0 OBJECT=0 PID=11 ROUTING=0 GROUP="" DPT="" VALUE="" COUNT=1 TIMEOUT=5 SECURE=0 SUSER=2 SUDP=0
while [ $# -gt 0 ]; do
	case "$1" in
	--target) TARGET=$2; shift ;;
	--port) PORT=$2; shift ;;
	--nat) NAT=1 ;;
	--routing) ROUTING=1 ;;
	--tcp) TCP=1 ;;
	--secure) SECURE=1 ;;
	--user) SUSER=$2; shift ;;
	--udp) SUDP=1 ;;
	--object) OBJECT=$2; shift ;;
	--pid) PID=$2; shift ;;
	--group) GROUP=$2; shift ;;
	--dpt) DPT=$2; shift ;;
	--value) VALUE=$2; shift ;;
	--count) COUNT=$2; shift ;;
	--timeout) TIMEOUT=${2%.*}; shift ;;
	--data | --name) shift ;;
	esac
	shift
done

host() {
	if [ "$ROUTING" = 1 ]; then
		echo 224.0.23.12
	else
		echo "$TARGET"
	fi
}
# The KNX Secure test profile (contract 1.2), from the Calimero keyfile
# and profile.json of /adapter/common/secure: public test values.
SEC=/adapter/common/secure
kf() { sed -n "s/^$1=//p" "$SEC/calimero.keyfile"; }
secure_opts() {
	kpw=$(sed -n 's/.*"keyringPassword": "\([^"]*\)".*/\1/p' "$SEC/profile.json")
	o="--keyring $SEC/knx-interop.knxkeys --keyring-pwd $kpw"
	if [ "$ROUTING" = 1 ]; then
		# 15.15.240 is the profile's routing source of Calimero tools.
		o="$o --group-key $(kf group.key) -k 15.15.240"
	else
		tr=--tcp
		[ "$SUDP" = 1 ] && tr=--udp
		o="$o $tr --user $SUSER --user-pwd $(kf "user\[$SUSER\].pwd") --device-key $(kf device.key)"
	fi
	echo "$o"
}
opts() {
	o="-p $PORT"
	if [ "$SECURE" = 1 ]; then
		echo "$o $(secure_opts)"
		return
	fi
	[ "$NAT" = 1 ] && o="$o --nat"
	[ "$TCP" = 1 ] && o="$o --tcp"
	echo "$o"
}
tools() { timeout "$((TIMEOUT + 10))" "$TOOLS" "$@" 2>&1 | grep -v '^WARNING: Unknown module'; }
# bgtools runs a tool in the background without a pipe (a pipe would
# buffer its output until it exits); the PID is the tool's own.
bgtools() { "$TOOLS" "$@" >/tmp/gm.log 2>&1 & P=$!; }

# groupmon_json converts groupmon --json objects to the contract's telegrams.
groupmon_json() {
	awk 'BEGIN{ORS=""; print "["; n=0}
		/"src":/ {split($0, a, "\""); src=a[4]}
		/"dst":/ {split($0, a, "\""); dst=a[4]; gsub(/\\/, "", dst)}
		/"svc":/ {split($0, a, "\""); svc=a[4]; sub(/A_Group\./, "", svc)}
		/"asdu":/ {split($0, a, "\""); asdu=toupper(a[4])}
		/^}/ { if (src != "") { if (n++) print ","; printf "{\"source\":\"%s\",\"group\":\"%s\",\"service\":\"%s\",\"data\":\"%s\"}", src, dst, svc, asdu }; src=""; dst=""; svc=""; asdu="" }
		END{print "]"}'
}

case "$ROLE" in
capabilities)
	printf '{"features":{"answer":false,"connect":true,"describe":true,"discover":true,"nat":true,"routing":true,"secure":true,"dataSecure":true,"secureUdp":true,"tunnel":true,"dptCodec":true,"tcp":true,"property":true,"busmonitor":true},"implementation":"%s","notes":"The Calimero process communication tool has no responder. Secure: tunnelling over TCP, routing and Data Secure with the test profile.","roles":["client"],"schemaVersion":"1.0","version":"%s"}\n' "$IMPL" "$VERSION"
	exit 0 ;;
server) finish unsupported '{}' "use the calimero-server adapter" ;;
client) ;;
*) echo "usage: run capabilities|client <op> ..." >&2; exit 2 ;;
esac

case "$OP" in
discover)
	out=$(tools discover search --json -t "$TIMEOUT")
	devs=$(printf '%s\n' "$out" | awk 'BEGIN{ORS=""; print "["; n=0}
		/"ctrlEndpoint":/ {split($0, a, "\""); ep=a[4]; gsub(/\\\//, "", ep); gsub(/\\/, "", ep); sub(/^\//, "", ep)}
		/"name":/ {split($0, a, "\""); name=a[4]}
		/"address":/ && ep != "" {split($0, a, "\""); if (n++) print ","; printf "{\"endpoint\":\"%s\",\"name\":\"%s\",\"address\":\"%s\"}", ep, name, a[4]; ep=""}
		END{print "]"}')
	finish pass "{\"devices\":$devs}" ;;
describe)
	# Text output: with --nat, calimero-tools 3.0-M1's JSON formatter throws
	# a NullPointerException (no network interface for the result).
	out=$(tools describe "$TARGET" $(opts))
	name=$(printf '%s\n' "$out" | sed -n 's/^"\(.*\)" *$/\1/p' | head -1)
	addr=$(printf '%s\n' "$out" | sed -n 's/^KNX address \([0-9.]*\).*/\1/p' | head -1)
	[ -z "$addr" ] && finish fail '{}' "$out"
	svcs=$(printf '%s\n' "$out" | sed -n 's/^Supported services: //p' | head -1 | tr ',' '\n' |
		sed -n 's/^ *\([A-Za-z ]*\) (v\([0-9]*\)).*/\1=\2/p' | awk -F= 'BEGIN{ORS=""; print "{"; n=0} {k=$1; gsub(/ /, "", k); if (k=="Tunneling") k="Tunnelling"; if (n++) print ","; printf "\"%s\":%s", k, $2} END{print "}"}')
	finish pass "{\"name\":\"$(json_str "$name")\",\"address\":\"$addr\",\"services\":$svcs}" ;;
connect)
	[ "$ROUTING" = 1 ] && finish unsupported '{}' "connect is for tunnels"
	if [ "$SECURE" = 1 ]; then
		# A killed groupmon leaves the secure user's tunnel (and its bound
		# address) open on the server; a read of an unused group connects
		# and disconnects normally.
		line=$(tools read 0/7/255 1.001 "$TARGET" $(opts) | grep -m1 "connection established")
		[ -z "$line" ] && finish fail '{}' "no secure connection"
		ch=$(echo "$line" | sed -n 's/.*channel \([0-9]*\).*/\1/p')
		ia=$(echo "$line" | sed -n 's/.*tunneling address \([0-9.]*\)).*/\1/p')
		finish pass "{\"channel\":${ch:-null},\"address\":\"$ia\"}"
	fi
	bgtools groupmon "$TARGET" $(opts)
	i=0
	while [ $i -lt $((TIMEOUT * 10)) ]; do
		line=$(grep -m1 "connection established" /tmp/gm.log)
		if [ -n "$line" ]; then
			kill $P 2>/dev/null
			ch=$(echo "$line" | sed -n 's/.*channel \([0-9]*\).*/\1/p')
			ia=$(echo "$line" | sed -n 's/.*tunneling address \([0-9.]*\)).*/\1/p')
			finish pass "{\"channel\":${ch:-null},\"address\":\"$ia\"}"
		fi
		grep -q "failed" /tmp/gm.log && { kill $P 2>/dev/null; finish fail '{}' "$(grep -v '^\s*at ' /tmp/gm.log | head -5)"; }
		i=$((i + 1))
		sleep 0.1
	done
	kill $P 2>/dev/null
	finish fail '{}' "no connection within ${TIMEOUT}s: $(head -5 /tmp/gm.log)" ;;
write)
	out=$(tools write "$GROUP" "$DPT" "$VALUE" "$(host)" $(opts))
	echo "$out" | grep -q "successful" || finish fail '{}' "$(echo "$out" | grep -E 'Exception|ERROR|failed' | head -3)"
	finish pass '{}' ;;
read)
	out=$(tools read "$GROUP" "$DPT" "$(host)" $(opts))
	line=$(echo "$out" | grep -m1 "value:")
	[ -z "$line" ] && finish fail '{}' "$(echo "$out" | grep -v '^\s*at ' | tail -3)"
	val=$(echo "$line" | sed 's/.*value: //')
	num=$(echo "$val" | sed -n 's/^\(-*[0-9][0-9.]*\).*/\1/p')
	if [ -n "$num" ]; then v=$num; else v="\"$(json_str "$val")\""; fi
	finish pass "{\"value\":$v,\"text\":\"$(json_str "$val")\"}" ;;
monitor)
	bgtools groupmon "$(host)" $(opts) --json
	i=0
	if [ "$ROUTING" = 1 ] && [ "$SECURE" = 1 ]; then
		# Secure routing: wait for the timer synchronisation (or the
		# tool becoming time keeper).
		while ! grep -q "synchronized" /tmp/gm.log && [ $i -lt 100 ]; do i=$((i + 1)); sleep 0.1; done
	elif [ "$ROUTING" = 1 ]; then
		sleep 3
	else
		while ! grep -q "connection established" /tmp/gm.log && [ $i -lt 100 ]; do i=$((i + 1)); sleep 0.1; done
	fi
	echo READY >&2
	i=0
	while [ $i -lt $((TIMEOUT * 10)) ]; do
		n=$(grep -c '"svc":' /tmp/gm.log)
		[ "$n" -ge "$COUNT" ] && break
		i=$((i + 1))
		sleep 0.1
	done
	sleep 0.2
	kill $P 2>/dev/null
	tel=$(groupmon_json </tmp/gm.log)
	n=$(grep -c '"svc":' /tmp/gm.log)
	[ "$n" -ge "$COUNT" ] && finish pass "{\"telegrams\":$tel}"
	finish fail "{\"telegrams\":$tel}" "received $n of $COUNT telegrams: $(grep -E 'ERROR|failed' /tmp/gm.log | head -3)" ;;
answer) finish unsupported '{}' "calimero-tools has no group responder" ;;
property)
	# The tool addresses interface objects by index; the device object is
	# index 0 on every server.
	[ "$OBJECT" = 0 ] || finish unsupported '{}' "the adapter reads the device object (index 0) only"
	out=$(tools get --local "$TARGET" $(opts) get 0 "$PID")
	data=$(printf '%s\n' "$out" | sed -n 's/.*(\([0-9a-fA-F]*\)).*/\1/p' | head -1 | tr a-f A-F)
	[ -n "$data" ] || finish fail '{}' "$(printf '%s\n' "$out" | grep -v '^\s*at ' | tail -3)"
	finish pass "{\"data\":\"$data\"}" ;;
busmonitor)
	bgtools monitor "$TARGET" $(opts)
	i=0
	while ! grep -q "connection established" /tmp/gm.log && [ $i -lt 100 ]; do i=$((i + 1)); sleep 0.1; done
	echo READY >&2
	i=0
	while [ $i -lt $((TIMEOUT * 10)) ]; do
		n=$(grep -c 'Busmon.ind' /tmp/gm.log)
		[ "$n" -ge "$COUNT" ] && break
		i=$((i + 1))
		sleep 0.1
	done
	kill $P 2>/dev/null
	frames=$(grep 'Busmon.ind' /tmp/gm.log | head -n "$COUNT" | sed -n 's/.*): \([0-9a-f ]*\) = .*/\1/p' |
		awk 'BEGIN{ORS=""; print "["} {gsub(/ /,""); if (NR>1) print ","; printf "{\"raw\":\"%s\"}", toupper($0)} END{print "]"}')
	n=$(grep -c 'Busmon.ind' /tmp/gm.log)
	[ "$n" -ge "$COUNT" ] && finish pass "{\"frames\":$frames}"
	finish fail "{\"frames\":$frames}" "received $n of $COUNT frames: $(grep -E 'ERROR|failed' /tmp/gm.log | head -3)" ;;
*) finish fail '{}' "unknown operation $OP" ;;
esac
