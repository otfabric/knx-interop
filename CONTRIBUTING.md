# Contributing to knx-interop

## Adding an implementation

1. It must be an independent protocol engine (not a wrapper of one already
   here) that runs headless on Linux amd64 and arm64.
2. Add `adapters/<name>/Dockerfile` (base image pinned by digest, upstream
   version pinned) and an entry point `/adapter/run` implementing
   [docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md), with an honest
   `capabilities` document: unsupported operations answer `unsupported`.
3. Add it to `versions.yaml` (with `published`), `THIRD_PARTY_NOTICES.md`, the
   Makefile's `ADAPTERS` and the runner's lists, and evaluate it in
   docs/CANDIDATES.md. A published image carries the licence texts of its
   components under `/licenses/<component>/`, which `scripts/smoke.py` checks.
4. Run `make images matrix` and add the results to docs/INTEROPERABILITY.md.

## OT Fabric's own stack

`own/go-knx/` is go-knx behind the contract, published by hand as
`knx-interop-otfabric` (`.github/workflows/own-go-knx.yml`). It is not a
reference and not in a release; nothing outside `own/` may name it or go-knx
(REQUIREMENTS.md R1, checked in CI). Build and test it with
`make -f own/go-knx/Makefile image smoke interop`.

## Rules

- A result is pass, fail, unsupported, not-tested or known-difference. A
  known difference needs a line in `tests/known-differences.tsv` with the
  evidence; never turn a failure into a pass.
- Fixtures are built from the standard's format rules (`make validate`
  recomputes them), not copied from specifications.
- Do not copy third-party code into the adapters; call the implementation.
- Shell adapters pass shellcheck; Python adapters use the standard library
  besides the stack under test.

## When CI runs

| Event | Workflow | What runs |
|---|---|---|
| Pull request | `pr.yml` | `policy.yml` (otfabric-policy) always; `ci.yml` unless every changed file is documentation; then `OT Fabric Required Checks` |
| Push to a branch | none | nothing; dispatch `ci.yml` to test a branch without a pull request |
| Push to `main` | `policy.yml` | the light checks; the merged commit was tested as the pull request's merge commit |
| Schedule | `ci.yml`, `upstream.yml` | the scheduled runs, on `main` |
| Release | `release.yml` | checks that `versions.yaml` and RELEASE.md name the version; on amd64 and arm64 builds the published images and runs `make smoke` on them before it pushes them; joins each image's two pushed digests into the multi-arch tag; creates the GitHub release with `manifest.json`. It runs no matrix and no `make validate` (both ran on the pull request) |

Documentation means an added or modified `*.md` file outside `.github/`, `testdata/` and `vendor/`, other than `AGENTS.md` and `CLAUDE.md`. A deleted or renamed document, or any other file, runs everything. `OT Fabric Required Checks` fails unless every job that applies succeeded; its summary lists them.
