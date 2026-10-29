# Security Policy

## Reporting a Vulnerability

Email **security@otfabric.io**, or open a private advisory on GitHub (the [Security](https://github.com/otfabric/knx-interop/security) tab). Do not open a public issue for security vulnerabilities. Vulnerabilities in the third-party implementations go to their projects.

## Scope

knx-interop runs KNX stacks in containers on an **isolated** user-defined
Docker bridge network created for each run, and removes it afterwards. Its
images open UDP port 3671 and join 224.0.23.12 inside that network only;
nothing is published on the host. The probe sends malformed datagrams: run
it only against servers you own.

No credentials or keys are used yet. When KNX IP Secure scenarios are
added, their keys will be test keys generated for the fixtures, never real
installation keys, and reports will not contain them.

Reports and logs contain container addresses and test telegrams only.
