#!/bin/sh
# SPDX-License-Identifier: MIT
# knx-interop adapter for calimero-server (GPL-2.0 with the Classpath
# exception): a KNXnet/IP server with an emulated KNX subnet, which keeps
# the last value written to each group address and answers reads with it.
set -u
VERSION=$(cat /adapter/VERSION)
ROLE=${1:-}
[ $# -gt 0 ] && shift
ROUTING=false NAME=knx-interop
while [ $# -gt 0 ]; do
	case "$1" in
	--routing) ROUTING=true ;;
	--name) NAME=$2; shift ;;
	esac
	shift
done
case "$ROLE" in
capabilities)
	printf '{"features":{"discover":true,"describe":true,"tunnel":true,"routing":true,"nat":true,"secure":false,"emulatedReads":true},"implementation":"calimero-server","notes":"The emulated subnet answers a read with the last value written; KNX IP Secure is supported by Calimero but not configured here yet.","roles":["server"],"schemaVersion":"1.0","version":"%s"}\n' "$VERSION"
	exit 0 ;;
server)
	group=""
	[ "$ROUTING" = true ] && group="<routing>224.0.23.12</routing>"
	sed -e "s|@NAME@|$NAME|; s|@ROUTING@|$ROUTING|; s|@ROUTING_GROUP@|$group|" /adapter/server-config.xml.in >/tmp/server-config.xml
	echo READY >&2
	cd /usr/app && exec calimero-server/bin/calimero-server --no-stdin /tmp/server-config.xml ;;
client) printf '{"data":{},"durationMs":0,"implementation":"calimero-server","op":"%s","schemaVersion":"1.0","status":"unsupported","version":"%s","error":"use the calimero-tools adapter"}\n' "${1:-}" "$VERSION"; exit 3 ;;
*) echo "usage: run capabilities|server" >&2; exit 2 ;;
esac
