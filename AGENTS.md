# AGENTS.md — knx-interop

## What this is

KNX over KNXnet/IP interoperability tests between independent implementations (Calimero, knxd, xknx, KNXUltimate, a raw probe) in containers on an isolated Docker network. A system under test such as go-knx brings its own adapter image; third-party images only here. Profile: **interoperability**.

## Organisation standards

This repository follows **otfabric/engineering policy 1.1**, profile **interoperability** (`.otfabric/policy.yaml`, mode `enforce`). Where this file and the organisation standards disagree, this file wins here — say so in your report.

## Where the truth lives

| Question | Source |
|---|---|
| Container commands, documents, exit codes | docs/CONTAINER_CONTRACT.md (`contract_version` in versions.yaml) |
| Pins (upstream revision, source hash, base image digests) | versions.yaml, checked by `make validate` |
| Expected deviations of the stacks | tests/known-differences.tsv |
| Results | docs/INTEROPERABILITY.md |

## Hard rules

1. Nothing floats: upstream sources and base images stay pinned, and versions.yaml mirrors the pins. `make validate` must pass.
2. Skips and known differences are never counted as passes.
3. An adapter answers an unsupported operation with the contract's unsupported error, never with a fake success.
4. Contract changes bump `contract_version` and reach every adapter and docs/CONTAINER_CONTRACT.md in the same change.
5. Licences: every redistributed component in THIRD_PARTY_NOTICES.md; images whose licence forbids redistribution are not published.
6. The release tag equals `interop_version`; bump versions.yaml before tagging.

## Commands

| When you change… | Run |
|---|---|
| anything | `make validate lint` |
| an adapter | `make image-<adapter> matrix-quick` |
| scenarios | `make matrix` |
| a release | `make release-notes VERSION=vX.Y.Z` |

## Git and releases

Branches and PRs. Do not push to `main`, push tags or publish images unless the maintainer asks in the session.
