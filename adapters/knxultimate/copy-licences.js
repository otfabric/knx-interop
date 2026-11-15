#!/usr/bin/env node
// SPDX-License-Identifier: MIT
// Copies the licence files of every package that package-lock.json installs
// to <dest>/<package path>/, in the image build (THIRD_PARTY_NOTICES.md):
//
//   node copy-licences.js <adapter dir> <dest>
//
// <package path> is the path under node_modules (a nested copy keeps its
// node_modules/ part, so two versions of one package do not collide).
// knxultimate itself must have one; a dependency without one is listed.
'use strict'

const fs = require('fs')
const path = require('path')

const LICENCE = /^(licen[cs]e|copying|notice)/i

function main (argv) {
  if (argv.length !== 2) {
    process.stderr.write('usage: copy-licences.js <adapter dir> <dest>\n')
    return 2
  }
  const [dir, dest] = argv
  const lock = JSON.parse(fs.readFileSync(path.join(dir, 'package-lock.json'), 'utf8'))
  const missing = []
  for (const key of Object.keys(lock.packages || {})) {
    if (!key.startsWith('node_modules/')) continue
    const src = path.join(dir, key)
    if (!fs.existsSync(src)) continue // optional or for another platform
    const files = fs.readdirSync(src).filter((f) => LICENCE.test(f) && fs.statSync(path.join(src, f)).isFile())
    if (files.length === 0) {
      missing.push(key)
      continue
    }
    const out = path.join(dest, key.slice('node_modules/'.length))
    fs.mkdirSync(out, { recursive: true })
    for (const f of files) fs.copyFileSync(path.join(src, f), path.join(out, f))
  }
  for (const key of missing) process.stdout.write(`${key}: no licence file in the package\n`)
  if (missing.includes('node_modules/knxultimate')) {
    process.stderr.write('knxultimate has no licence file\n')
    return 1
  }
  return 0
}

process.exitCode = main(process.argv.slice(2))
