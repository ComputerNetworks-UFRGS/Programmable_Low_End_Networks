# Vegan Internet - LoRa Programmable Networks

This folder contains the documentation and GNU Radio structure used to reproduce the TCC experiment.

The project combines BMv2, p4c, GNU Radio, USRP/UHD devices, TAP interfaces, and basic validation tests.

## Folder Structure

```text
tcc-lora-programmable-networks/
│   README.md
│
├── docs/
│   ├── reference/
│   │   └── consolidated-install-guide.md
│   │
│   ├── setup/
│   │   ├── README.md
│   │   ├── 01-system-dependencies.md
│   │   ├── 02-source-preparation.md
│   │   ├── 03-build-bmv2-behavioral-model.md
│   │   └── 04-build-p4c.md
│   │
│   ├── gnuradio/
│   │   ├── README.md
│   │   ├── 01-tap-interface-setup.md
│   │   ├── 02-gnu-radio-and-usrp.md
│   │   └── 03-running-the-grc-flowgraphs.md
│   │
│   ├── validation/
│   │   ├── 01-p4-bmv2-end-to-end-validation.md
│   │   └── 02-basic-execution-tests.md
│   │
│   └── troubleshooting/
│       └── README.md
│
└── gnuradio/
    ├── README.md
    ├── VM1/
    │   └── README.md
    └── VM2/
        └── README.md
```

## Recommended Reading Order

1. `docs/setup/README.md`
2. `docs/setup/01-system-dependencies.md`
3. `docs/setup/02-source-preparation.md`
4. `docs/setup/03-build-bmv2-behavioral-model.md`
5. `docs/setup/04-build-p4c.md`
6. `docs/gnuradio/README.md`
7. `docs/gnuradio/03-running-the-grc-flowgraphs.md`
8. `docs/validation/02-basic-execution-tests.md`

## GNU Radio Flowgraphs

Add the `.grc` files here:

```text
gnuradio/VM1/vm1-vegan-internet.grc
gnuradio/VM2/vm2-vegan-internet.grc
```

## Basic Execution Summary

### VM1

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.1/24
sudo ip link set dev tap0 up
sudo uhd_find_devices
sudo gnuradio-companion gnuradio/VM1/vm1-vegan-internet.grc
```

### VM2

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.2/24
sudo ip link set dev tap0 up
sudo uhd_find_devices
sudo gnuradio-companion gnuradio/VM2/vm2-vegan-internet.grc
```

After both flowgraphs are running, execute the tests in:

```text
docs/validation/02-basic-execution-tests.md
```
