# Independent KNX implementations: evaluation

Evaluated 2026-10-29 from upstream sources, release metadata and running
the images. "Independent" means a separate protocol engine: wrappers of the
same engine count once.

| Candidate | Licence | Language | Version evaluated | Engine / lineage | Server | Client | Routing | IP Secure | Data Secure | Headless in CI | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Calimero** (calimero-core, -server, -tools) | GPL-2.0 with Classpath exception | Java | server/tools 3.0-M1 images; 3.0-M2 tags (core `fd3c60f2`, server `5f162f26`, tools `60d7fbe4`) 2026-04-04 | Calimero core | yes: UDP and TCP tunnelling v1/v2, discovery incl. extended search, routing, busmonitor, device management, emulated subnet | yes: tools discover, describe, read, write, groupmon (`--json`) | yes | yes (tunnelling, routing) | yes | official multi-arch images | **used** (server and client) |
| **knxd** + knxtool | GPL-2.0 | C++ | Debian trixie 0.14.73-1 (upstream tag 0.14.75 `5b5514c3`) | knxd | yes: UDP tunnelling, discovery (no extended search), routing; TCP tunnelling server ≥ 0.14.68 | yes: `ipt`/`iptn` tunnel client, `ip` routing, knxtool | yes | no | no | Debian package, amd64/arm64 | **used** (server and client) |
| **xknx** | MIT | Python | 4.0.0 (`bdf5ea45`, 2026-10-15) | xknx | no | yes: UDP/TCP tunnelling, route back, discovery incl. extended search | yes | yes | yes | pip, pure Python | **used** (client) |
| **KNXUltimate** | MIT | TypeScript | 6.3.1 (`ad9bc2c8`, 2026-10-28) | KNXUltimate | minimal UDP tunnel server (no discovery) | yes: UDP/TCP tunnelling, discovery, description | yes | yes | yes | npm | **used** (client) |
| **openHAB KNX binding** | EPL-2.0 | Java | 5.2.3 / 5.3.0.M3 | **embeds calimero-core 3.0-M2** | — | — | — | — | — | needs an openHAB runtime | **rejected**: same engine as Calimero |
| knx-go (vapourismo) | MIT | Go | no tags, last commit 2026-08-13, "no longer maintained" | knx-go | no | yes | yes | no | no | yes | watch list: unmaintained, same language as go-knx |
| knx.js (ekarak, npm `knx`) | MIT | JavaScript | 2.5.4 (2024) | knx.js | no | yes | yes | no | no | yes | rejected: stale, superseded by KNXUltimate |
| knx-rs (metaneutrons) | GPL-3.0 | Rust | v0.12.0 (`b53faedb`, 2026-10-29) | knx-rs | tunnel server without search/description | yes | yes | — | — | yes | watch list: six months old |
| knust (dphi) | MIT | Rust | v0.2.0 | knust | UDP/TCP tunnel server | yes | yes | yes | experimental | yes | watch list: very young |
| OpenKNX / thelsing knx | GPL-3.0 | C++ | v1 branch | device stack | needs a Linux host program | — | — | — | — | no ready program | rejected for now |
| KNX Virtual | proprietary | .NET (Windows GUI) | — | KNX Association | — | — | — | — | — | no | not usable in CI |
| Knx.Falcon.Sdk | proprietary | .NET | 6.4.x | KNX Association | — | — | — | — | — | licence unclear | not usable |

Five candidates of the task were evaluated (Calimero, knxd, xknx,
KNXUltimate, openHAB); four are independent engines and are used. openHAB
was rejected because it is Calimero.

## Adapter notes

- **Calimero**: the images are the official ones pinned by digest (3.0-M1,
  the newest with images). The tools try a device management connection
  after a tunnel; a server without it logs an error, harmlessly. With
  `--nat`, `describe --json` throws in Calimero's JSON formatter, so the
  adapter parses the text output.
- **knxd**: the Debian package has no `eibnetsearch`/`eibnetdescribe`, so
  discovery and description are unsupported through this adapter. knxd has
  no DPT codec: writes take the expected octets (`--data`). As a tunnel
  client it would send its own client addresses (1.2.10…) as sources; the
  adapter uses knxd's `single` filter, which sends with the address the
  server assigned. Without it, knxd's own server drops a source address it
  learned on an earlier connection.
- **xknx**: no server. Scripts drive `xknx.XKNX` directly (tunnelling,
  routing, route back, value reader, telegram callbacks).
- **KNXUltimate**: no route back option; its describe announces the wrong
  port (known difference).
