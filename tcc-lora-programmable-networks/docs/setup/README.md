# Setup documentation

This section contains the installation flow for the P4Pi environment.

The goal is to avoid duplicated installation commands across multiple files. All system packages are listed only once in:

- [`01-system-dependencies.md`](01-system-dependencies.md)

After that, each setup file assumes the dependencies are already installed.

## Execution order

1. [`01-system-dependencies.md`](01-system-dependencies.md)
2. [`02-source-preparation.md`](02-source-preparation.md)
3. [`03-build-bmv2-behavioral-model.md`](03-build-bmv2-behavioral-model.md)
4. [`04-build-p4c.md`](04-build-p4c.md)

## Components installed

- BMv2 / `behavioral-model`
- `simple_switch`
- `simple_switch_CLI`
- `p4c`
- `p4c-bm2-ss`
- P4 include files such as `v1model.p4`
