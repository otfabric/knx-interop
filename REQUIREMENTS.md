# Requirements

What this repository must do and must not do.
[docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md) is the
specification that follows from it.

## Purpose

Independent, reproducible interoperability validation for KNX over
KNXnet/IP: established third-party implementations, packaged as containers
that behave the same way, so that a library can be tested against
implementations it does not own.

It is not another KNX implementation and not a general protocol-testing
framework.

## R1 - Repository isolation

- R1.1 This repository does not import, build, link against or depend on any
  library under test, and contains no test logic or expectation specific to
  one. The one exception is `own/` with its workflow: images of OT Fabric's own
  stacks, published for others to test against (`own/go-knx/README.md`). The
  rest of the repository does not know them, and they are not part of a release.
  CI fails when `adapters/`, `fixtures/`, `schemas/`, `scenarios/`, `scripts/`,
  `tests/`, the `Makefile` or `compose.yaml` name go-knx or knxctl.
- R1.2 A system under test brings its own adapter image and depends on the
  published images, the documented contract and the matrix runner only.
- R1.3 No third-party code from here is copied into a consumer, and the
  contract does not shape a consumer's public API.

| Responsibility | Here | Consumer |
|----------------|:----:|:--------:|
| Third-party implementations, adapters, Dockerfiles | yes | no |
| Fixtures, the KNX Secure test profile | yes | no |
| Container contract, capability declarations | yes | no |
| Image builds and publishing, licence compliance | yes | no |
| The scenarios between the stacks (`scripts/run-matrix.py`) | yes | no |
| Its own adapter image, scenarios and assertions about a library | no | yes |
| Compatibility claims and release qualification of a library | no | yes |

## R2 - Reference implementations

- R2.1 In scope: Calimero (server and tools), knxd, xknx, KNXUltimate, and a
  probe of hand-built datagrams for negative tests (`versions.yaml`).
- R2.2 Each implementation is its own image. No image contains two.
- R2.3 An adapter uses the implementation's public API or tools as an
  application would. It does not patch the implementation: what a stack
  cannot do is declared `false` in its capabilities and answered
  `unsupported`.

## R3 - One contract

- R3.1 Every image has the same commands, options, documents and exit codes
  ([docs/CONTAINER_CONTRACT.md](docs/CONTAINER_CONTRACT.md)); a smoke test
  checks each image on its own (`scripts/smoke.sh`).
- R3.2 Every wait is bounded. stdout carries the result documents;
  diagnostics go to stderr.

## R4 - Honest results

- R4.1 A result is pass, fail, unsupported, not-tested or known-difference;
  only pass counts as passing. A known difference needs its evidence in
  [tests/known-differences.tsv](tests/known-differences.tsv), and a waiver
  that no longer reproduces fails the run.

## R5 - Reproducibility

- R5.1 Upstreams are pinned by exact version, images and base images by
  digest; [versions.yaml](versions.yaml) mirrors every pin and
  `make validate` fails when it disagrees with the build files.
- R5.2 Images are built natively for linux/amd64 and linux/arm64 and tested
  on both before they are published.

## R6 - Licensing

- R6.1 The repository's own code is MIT-licensed.
- R6.2 Images that contain GPL binaries (Calimero, knxd) are never
  published; they are built from their Dockerfiles where they are used
  ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
