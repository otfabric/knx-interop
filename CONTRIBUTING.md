# Contributing to knx-interop

## Adding an implementation

1. It must be an independent protocol engine (not a wrapper of one already
   here) that runs headless on Linux amd64 and arm64.
2. Add `adapters/<name>/Dockerfile` (base image pinned by digest, upstream
   version pinned) and an entry point `/adapter/run` implementing
   [docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md), with an honest
   `capabilities` document: unsupported operations answer `unsupported`.
3. Add it to `versions.yaml`, `THIRD_PARTY_NOTICES.md`, the Makefile's
   `ADAPTERS` and the runner's lists, and evaluate it in docs/CANDIDATES.md.
4. Run `make images matrix` and add the results to docs/INTEROPERABILITY.md.

## Rules

- A result is pass, fail, unsupported, not-tested or known-difference. A
  known difference needs a line in `tests/known-differences.tsv` with the
  evidence; never turn a failure into a pass.
- Fixtures are built from the standard's format rules (`make validate`
  recomputes them), not copied from specifications.
- Do not copy third-party code into the adapters; call the implementation.
- Shell adapters pass shellcheck; Python adapters use the standard library
  besides the stack under test.
