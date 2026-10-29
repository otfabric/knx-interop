#!/usr/bin/env node
// SPDX-License-Identifier: MIT
// knx-interop adapter for KNXUltimate (Supergiovane/KNXUltimate, MIT): client
// roles over UDP tunnelling and routing.
'use strict'

const { KNXClient, KNXClientEvents, dptlib } = require('knxultimate')
const pkg = require('knxultimate/package.json')

const IMPL = 'knxultimate'
const VERSION = pkg.version
const start = Date.now()

function parse(argv) {
  const a = { role: argv[0], op: '', target: '', port: 3671, nat: false, routing: false, group: '', dpt: '', value: '', data: '', count: 1, timeout: 5 }
  let i = 1
  if (a.role === 'client') { a.op = argv[1]; i = 2 }
  for (; i < argv.length; i++) {
    const k = argv[i]
    const v = argv[i + 1]
    switch (k) {
      case '--target': a.target = v; i++; break
      case '--port': a.port = Number(v); i++; break
      case '--nat': a.nat = true; break
      case '--routing': a.routing = true; break
      case '--group': a.group = v; i++; break
      case '--dpt': a.dpt = v; i++; break
      case '--value': a.value = v; i++; break
      case '--data': a.data = v; i++; break
      case '--count': a.count = Number(v); i++; break
      case '--timeout': a.timeout = Number(v); i++; break
      case '--name': i++; break
    }
  }
  return a
}

const args = parse(process.argv.slice(2))
let client = null

function finish(status, data, error) {
  const doc = { data: data || {}, durationMs: Date.now() - start, implementation: IMPL, op: args.op || args.role, schemaVersion: '1.0', status, version: VERSION }
  if (error) doc.error = String(error).slice(0, 2000)
  process.stdout.write(JSON.stringify(doc) + '\n')
  const code = { pass: 0, fail: 1, unsupported: 3 }[status]
  const exit = () => process.exit(code)
  if (client) {
    Promise.resolve().then(() => client.Disconnect()).catch(() => {}).finally(() => setTimeout(exit, 300))
    setTimeout(exit, 3000)
  } else exit()
}

function jsValue(dpt, value) {
  if (dpt.startsWith('1.')) return ['1', 'on', 'true'].includes(value.toLowerCase())
  if (dpt.startsWith('16.') || dpt.startsWith('4.')) return value
  return Number(value)
}

function hex(buf) { return buf ? Buffer.from(buf).toString('hex').toUpperCase() : '' }

function service(npdu) {
  if (npdu.isGroupWrite) return 'write'
  if (npdu.isGroupResponse) return 'response'
  if (npdu.isGroupRead) return 'read'
  return 'other'
}

function connect() {
  return new Promise((resolve, reject) => {
    const opts = { ipAddr: args.routing ? '224.0.23.12' : args.target, ipPort: String(args.port), hostProtocol: args.routing ? 'Multicast' : 'TunnelUDP', physAddr: '1.3.250', suppress_ack_ldatareq: false, loglevel: 'error' }
    client = new KNXClient(opts)
    const t = setTimeout(() => reject(new Error(`no connection within ${args.timeout}s`)), args.timeout * 1000)
    client.on(KNXClientEvents.connected, () => { clearTimeout(t); resolve() })
    client.on(KNXClientEvents.error, (e) => { clearTimeout(t); reject(e) })
    client.Connect()
  })
}

async function main() {
  if (args.role === 'capabilities') {
    process.stdout.write(JSON.stringify({ features: { answer: true, connect: true, describe: true, discover: true, nat: false, routing: true, secure: false, tunnel: true, dptCodec: true }, implementation: IMPL, notes: 'KNXUltimate supports KNX IP Secure and Data Secure; this adapter does not exercise them yet. It has no route back (NAT) option.', roles: ['client'], schemaVersion: '1.0', version: VERSION }) + '\n')
    return
  }
  if (args.role === 'server') return finish('unsupported', {}, 'the adapter uses KNXUltimate as a client only')
  if (args.nat) return finish('unsupported', {}, 'KNXUltimate has no route back (NAT) option')
  switch (args.op) {
    case 'discover': {
      const list = await KNXClient.discover(args.timeout * 1000)
      const devices = list.map((s) => { const [ip, port, name, address] = String(s).split(':'); return { endpoint: `${ip}:${port}`, name, address } })
      return finish('pass', { devices })
    }
    case 'describe': {
      const ds = await KNXClient.getGatewayDescription(args.target, String(args.port), args.timeout * 1000)
      if (!ds.length) return finish('fail', {}, 'no description response')
      const d = ds[0]
      const info = d.deviceInfo || {}
      const services = {}
      for (const f of (d.supportedFamilies || d.serviceFamilies || {}).services || []) services[f.name || f.id] = f.version
      return finish('pass', { name: String(info.name || '').replace(/\0+$/, ''), address: info.formattedAddress || String(info.address || ''), services })
    }
  }
  await connect()
  switch (args.op) {
    case 'connect':
      return finish('pass', { channel: client._channelID ?? null, address: client.physAddr ? client.physAddr.toString() : '' })
    case 'write':
      client.write(args.group, jsValue(args.dpt, args.value), args.dpt)
      await new Promise((r) => setTimeout(r, 1000))
      return finish('pass', {})
    case 'read':
    case 'monitor':
    case 'answer': {
      const telegrams = []
      let answered = 0
      const done = new Promise((resolve) => {
        client.on(KNXClientEvents.indication, (datagram) => {
          const c = datagram.cEMIMessage
          if (!c || !c.dstAddress) return
          const g = c.dstAddress.toString()
          const t = { source: c.srcAddress.toString(), group: g, service: service(c.npdu), data: hex(c.npdu.dataValue) }
          if (args.op === 'monitor') { telegrams.push(t); if (telegrams.length >= args.count) resolve() }
          if (args.op === 'read' && g === args.group && t.service === 'response') { telegrams.push(t); resolve() }
          if (args.op === 'answer' && g === args.group && t.service === 'read') {
            const cfg = dptlib.resolve(args.dpt)
            client.respond(args.group, jsValue(args.dpt, args.value), args.dpt)
            answered++
            if (answered >= args.count) setTimeout(resolve, 500)
            void cfg
          }
        })
      })
      const timer = new Promise((resolve) => setTimeout(resolve, args.timeout * 1000))
      if (args.op !== 'read') process.stderr.write('READY\n')
      if (args.op === 'read') client.read(args.group)
      await Promise.race([done, timer])
      if (args.op === 'answer') return finish('pass', { answered })
      if (args.op === 'read') {
        if (!telegrams.length) return finish('fail', {}, `no response within ${args.timeout}s`)
        const t = telegrams[0]
        let value = null
        try { value = dptlib.fromBuffer(Buffer.from(t.data, 'hex'), dptlib.resolve(args.dpt)) } catch (e) { void e }
        return finish('pass', { source: t.source, data: t.data, value })
      }
      const ok = telegrams.length >= args.count
      return finish(ok ? 'pass' : 'fail', { telegrams }, ok ? undefined : `received ${telegrams.length} of ${args.count} telegrams`)
    }
  }
  return finish('fail', {}, `unknown operation ${args.op}`)
}

main().catch((e) => finish('fail', {}, e && e.stack ? e.stack : e))
