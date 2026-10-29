#!/bin/sh
# SPDX-License-Identifier: MIT
# knx-interop adapter for knxd (GPL-2.0) and knxtool: server, and tunnelling
# or routing client through a local knxd daemon.
set -u

IMPL=knxd
VERSION=$(knxd --version 2>&1 | head -1 | sed "s/^knxd //")
START=$(date +%s%3N)

json_str() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n\t' '  '; }

finish() { # status data-json [error]
	now=$(date +%s%3N)
	err=""
	[ $# -ge 3 ] && err=$(printf ',"error":"%s"' "$(json_str "$3")")
	printf '{"data":%s,"durationMs":%d,"implementation":"%s","op":"%s","schemaVersion":"1.0","status":"%s","version":"%s"%s}\n' \
		"$2" $((now - START)) "$IMPL" "$OP" "$1" "$VERSION" "$err"
	stop_daemon
	case "$1" in pass) exit 0 ;; unsupported) exit 3 ;; *) exit 1 ;; esac
}

ready() { echo READY >&2; }

ROLE=${1:-}
[ $# -gt 0 ] && shift
OP=$ROLE
if [ "$ROLE" = client ]; then OP=${1:-}; shift; fi
TARGET="" PORT=3671 NAT=0 ROUTING=0 GROUP="" DPT="" VALUE="" DATA="" COUNT=1 TIMEOUT=5 NAME=knx-interop
while [ $# -gt 0 ]; do
	case "$1" in
	--target) TARGET=$2; shift ;;
	--port) PORT=$2; shift ;;
	--nat) NAT=1 ;;
	--routing) ROUTING=1 ;;
	--group) GROUP=$2; shift ;;
	--dpt) DPT=$2; shift ;;
	--value) VALUE=$2; shift ;;
	--data) DATA=$2; shift ;;
	--count) COUNT=$2; shift ;;
	--timeout) TIMEOUT=${2%.*}; shift ;;
	--name) NAME=$2; shift ;;
	esac
	shift
done

DAEMON=""
stop_daemon() { [ -n "$DAEMON" ] && kill "$DAEMON" 2>/dev/null && wait "$DAEMON" 2>/dev/null; DAEMON=""; }
SOCK=local:/tmp/knx

# start_daemon starts knxd as a client of the target (tunnel or routing)
# with a local socket for knxtool.
start_daemon() {
	filt=""
	if [ "$ROUTING" = 1 ]; then
		drv="ip:224.0.23.12:3671"
	elif [ "$NAT" = 1 ]; then
		drv="iptn:$TARGET:$PORT"
	else
		drv="ipt:$TARGET:$PORT"
	fi
	# Tunnels: the "single" filter sends with the address the server
	# assigned, not knxd's own client addresses (1.2.10...): a server may
	# drop a source address it learned on an earlier connection (knxd's
	# server does, as loop protection).
	[ "$ROUTING" = 1 ] || filt="-B single"
	rm -f /tmp/knx
	knxd -e 1.2.0 -E 1.2.10:4 -u /tmp/knx $filt -b "$drv" >/tmp/knxd.log 2>&1 &
	DAEMON=$!
	i=0
	while [ ! -S /tmp/knx ]; do
		i=$((i + 1))
		[ $i -gt 50 ] && finish fail '{}' "knxd did not open its socket: $(cat /tmp/knxd.log)"
		kill -0 "$DAEMON" 2>/dev/null || finish fail '{}' "knxd exited: $(cat /tmp/knxd.log)"
		sleep 0.1
	done
	# The tunnel is set up after the socket opens.
	sleep 1
	kill -0 "$DAEMON" 2>/dev/null || finish fail '{}' "knxd exited: $(cat /tmp/knxd.log)"
}

# hexbytes "0C33" -> "0c 33"
hexbytes() { printf '%s' "$1" | sed 's/../& /g; s/ $//'; }

case "$ROLE" in
capabilities)
	printf '{"features":{"answer":true,"connect":true,"describe":false,"discover":false,"nat":true,"routing":true,"secure":false,"tunnel":true,"dptCodec":false},"implementation":"%s","notes":"The Debian package has no eibnetsearch/eibnetdescribe tools; knxd has no DPT codec, writes send the octets given with --data.","roles":["server","client"],"schemaVersion":"1.0","version":"%s"}\n' "$IMPL" "$VERSION"
	exit 0 ;;
server)
	r=""
	[ "$ROUTING" = 1 ] && r="-R"
	ready
	exec knxd -n "$NAME" -e 1.1.0 -E 1.1.10:8 -D -T $r -S -b dummy: ;;
client) ;;
*) echo "usage: run capabilities|server|client <op> ..." >&2; exit 2 ;;
esac

case "$OP" in
discover | describe)
	finish unsupported '{}' "the Debian knxd package has no KNXnet/IP search or description tool" ;;
connect)
	[ "$ROUTING" = 1 ] && finish unsupported '{}' "connect is for tunnels"
	start_daemon
	finish pass '{}' ;;
write)
	[ -z "$DATA" ] && finish unsupported '{}' "knxd has no DPT codec: --data is required"
	start_daemon
	case "$DPT" in
	1.* | 2.* | 3.*) out=$(knxtool groupswrite "$SOCK" "$GROUP" "$((0x$DATA))" 2>&1) ;;
	*) out=$(knxtool groupwrite "$SOCK" "$GROUP" $(hexbytes "$DATA") 2>&1) ;;
	esac
	rc=$?
	sleep 0.5
	[ $rc -eq 0 ] || finish fail '{}' "$out"
	finish pass "{\"data\":\"$DATA\"}" ;;
read)
	start_daemon
	knxtool groupsocketlisten "$SOCK" >/tmp/listen.log 2>&1 &
	L=$!
	sleep 0.3
	knxtool groupread "$SOCK" "$GROUP" >/dev/null 2>&1
	i=0
	while [ $i -lt $((TIMEOUT * 10)) ]; do
		line=$(grep -m1 "Response from .* to $GROUP:" /tmp/listen.log)
		if [ -n "$line" ]; then
			kill $L 2>/dev/null
			src=$(echo "$line" | sed -n 's/^Response from \([0-9.]*\) to .*/\1/p')
			hex=$(echo "$line" | sed 's/^[^:]*: *//; s/ //g' | tr a-f A-F)
			finish pass "{\"source\":\"$src\",\"data\":\"$hex\"}"
		fi
		i=$((i + 1))
		sleep 0.1
	done
	kill $L 2>/dev/null
	finish fail '{}' "no response within ${TIMEOUT}s" ;;
monitor)
	start_daemon
	knxtool groupsocketlisten "$SOCK" >/tmp/listen.log 2>&1 &
	L=$!
	sleep 0.3
	ready
	i=0
	while [ $i -lt $((TIMEOUT * 10)) ]; do
		n=$(grep -cE '^(Write|Read|Response) from' /tmp/listen.log)
		[ "$n" -ge "$COUNT" ] && break
		i=$((i + 1))
		sleep 0.1
	done
	kill $L 2>/dev/null
	tel=$(grep -E '^(Write|Read|Response) from' /tmp/listen.log | head -n "$COUNT" | sed -n 's/^\([A-Za-z]*\) from \([0-9.]*\) to \([0-9/]*\):* *\(.*\)$/\1|\2|\3|\4/p' |
		awk -F'|' 'BEGIN{ORS=""; print "["} {gsub(/ /,"",$4); s=tolower($1); if (NR>1) print ","; printf "{\"source\":\"%s\",\"group\":\"%s\",\"service\":\"%s\",\"data\":\"%s\"}", $2, $3, s, toupper($4)} END{print "]"}')
	n=$(grep -cE '^(Write|Read|Response) from' /tmp/listen.log)
	[ "$n" -ge "$COUNT" ] && finish pass "{\"telegrams\":$tel}"
	finish fail "{\"telegrams\":$tel}" "received $n of $COUNT telegrams" ;;
answer)
	[ -z "$DATA" ] && finish unsupported '{}' "knxd has no DPT codec: --data is required"
	start_daemon
	knxtool groupsocketlisten "$SOCK" >/tmp/listen.log 2>&1 &
	L=$!
	sleep 0.3
	ready
	answered=0 seen=0 i=0
	while [ $i -lt $((TIMEOUT * 10)) ] && [ $answered -lt "$COUNT" ]; do
		n=$(grep -c "^Read from .* to $GROUP" /tmp/listen.log)
		while [ $seen -lt "$n" ]; do
			seen=$((seen + 1))
			case "$DPT" in
			1.* | 2.* | 3.*) knxtool groupsresponse "$SOCK" "$GROUP" "$((0x$DATA))" >/dev/null 2>&1 ;;
			*) knxtool groupresponse "$SOCK" "$GROUP" $(hexbytes "$DATA") >/dev/null 2>&1 ;;
			esac
			answered=$((answered + 1))
		done
		i=$((i + 1))
		sleep 0.1
	done
	kill $L 2>/dev/null
	sleep 0.3
	finish pass "{\"answered\":$answered}" ;;
*) finish fail '{}' "unknown operation $OP" ;;
esac
