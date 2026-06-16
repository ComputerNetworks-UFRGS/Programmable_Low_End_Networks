# TCC LoRa Programmable Networks Documentation

This folder contains the documentation required to reproduce the P4Pi setup used in the TCC project.

The documentation is intentionally organized by stage, so future GNU Radio files, P4 programs, experiments, and scripts can be added later without mixing them with setup notes.

## Recommended reading order

1. [`docs/setup/README.md`](docs/setup/README.md)  
   Overview of the installation flow.

2. [`docs/setup/01-system-dependencies.md`](docs/setup/01-system-dependencies.md)  
   Single source of truth for all system packages required by BMv2 and P4C.

3. [`docs/setup/02-source-preparation.md`](docs/setup/02-source-preparation.md)  
   Clone the P4Pi project, run `cpfiles.sh`, and prepare the BMv2/P4C sources.

4. [`docs/setup/03-build-bmv2-behavioral-model.md`](docs/setup/03-build-bmv2-behavioral-model.md)  
   Build and install BMv2 / `behavioral-model`, including `simple_switch` and `simple_switch_CLI`.

5. [`docs/setup/04-build-p4c.md`](docs/setup/04-build-p4c.md)  
   Build and install `p4c`, including `p4c-bm2-ss`.

6. [`docs/validation/01-p4-bmv2-end-to-end-validation.md`](docs/validation/01-p4-bmv2-end-to-end-validation.md)  
   Validate the setup by compiling a P4 program, running `simple_switch`, and connecting through `simple_switch_CLI`.

7. [`docs/troubleshooting/README.md`](docs/troubleshooting/README.md)  
   Known errors and fixes found during the setup.

## Reference

A consolidated version is available at:

- [`docs/reference/consolidated-install-guide.md`](docs/reference/consolidated-install-guide.md)

Use the staged documents for execution. Use the consolidated guide only as a quick reference.

## Versions used

| Component | Repository | Commit |
|---|---|---|
| BMv2 / behavioral-model | `https://github.com/p4lang/behavioral-model` | `f745e1db5e281d1e30483496c3c0960a8d23c852` |
| P4C | `https://github.com/p4lang/p4c` | `1576090b74b610e979a3afeafec79d0a2f81a598` |
| P4Pi project | `https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks/tree/main/p4pi` | main branch |

## Default project path

The commands assume the following path:

```bash
export P4PI_DIR="$HOME/p4c/Programmable_Low_End_Networks/p4pi"
```

If the project is cloned somewhere else, update `P4PI_DIR` before running the commands.
