#!/bin/sh
# SPDX-License-Identifier: MIT
# knx-interop adapter for calimero-server (GPL-2.0 with the Classpath
# exception): a KNXnet/IP server with an emulated KNX subnet, which keeps
# the last value written to each group address and answers reads with it.
# Option lists ($(opts), $filt, hex octets) are split on purpose; some
# parsed options are not used by every role.
# shellcheck disable=SC2046,SC2086,SC2034
set -u
VERSION=$(cat /adapter/VERSION)
ROLE=${1:-}
[ $# -gt 0 ] && shift
ROUTING=false NAME=knx-interop SECURE=0
while [ $# -gt 0 ]; do
	case "$1" in
	--routing) ROUTING=true ;;
	--name) NAME=$2; shift ;;
	--secure) SECURE=1 ;;
	esac
	shift
done
case "$ROLE" in
capabilities)
	printf '{"features":{"discover":true,"describe":true,"tunnel":true,"routing":true,"nat":true,"secure":true,"emulatedReads":true,"server":{"tcp":true,"property":true,"busmonitor":false,"secure":true,"secureUdp":true,"secureRouting":true}},"implementation":"calimero-server","notes":"The emulated subnet answers a read with the last value written; a busmonitor connection is exclusive and the emulated subnet sends nothing while it is open. --secure: secure tunnelling and device management with the test profile (keyfile; users 2 and 3 bound to 1.1.10 and 1.1.11, user 1 management).","roles":["server"],"schemaVersion":"1.0","version":"%s"}\n' "$VERSION"
	exit 0 ;;
server)
	group=""
	[ "$ROUTING" = true ] && group="<routing>224.0.23.12</routing>"
	secure="" users=""
	if [ "$SECURE" = 1 ]; then
		services=devmgmt,tunneling
		if [ "$ROUTING" = true ]; then
			services=$services,routing
			# Secure routing needs the profile's latency tolerance.
			group='<routing latencyTolerance="1000">224.0.23.12</routing>'
			# calimero-server 3.0-M1's secure routing service reflects into
			# io.calimero.knxnetip, which the core module does not open.
			export JDK_JAVA_OPTIONS="--add-opens io.calimero.core/io.calimero.knxnetip=io.calimero.server"
		fi
		secure="keyfile=\"/adapter/common/secure/calimero.keyfile\" securedServices=\"$services\""
		users='<tunnelingUsers><user id="2"><knxAddress type="individual">1.1.10</knxAddress></user><user id="3"><knxAddress type="individual">1.1.11</knxAddress></user></tunnelingUsers>'
	fi
	sed -e "s|@NAME@|$NAME|; s|@ROUTING@|$ROUTING|; s|@ROUTING_GROUP@|$group|; s|@SECURE@|$secure|; s|@USERS@|$users|" /adapter/server-config.xml.in >/tmp/server-config.xml
	echo READY >&2
	cd /usr/app && exec calimero-server/bin/calimero-server --no-stdin /tmp/server-config.xml ;;
client) printf '{"data":{},"durationMs":0,"implementation":"calimero-server","op":"%s","schemaVersion":"1.0","status":"unsupported","version":"%s","error":"use the calimero-tools adapter"}\n' "${1:-}" "$VERSION"; exit 3 ;;
*) echo "usage: run capabilities|server" >&2; exit 2 ;;
esac
