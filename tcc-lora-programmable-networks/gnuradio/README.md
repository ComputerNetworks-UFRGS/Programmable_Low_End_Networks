# GNU Radio Flowgraphs

This folder stores the GNU Radio Companion `.grc` files used by the experiment.

## Structure

```text
gnuradio/
├── README.md
├── VM1/
│   ├── README.md
│   └── vm1-vegan-internet.grc
└── VM2/
    ├── README.md
    └── vm2-vegan-internet.grc
```

## Recommended File Names

```text
VM1/vm1-vegan-internet.grc
VM2/vm2-vegan-internet.grc
```

These names avoid spaces and uppercase letters in the file path while keeping the project name clear.

## Running

From the project root:

```bash
sudo gnuradio-companion gnuradio/VM1/vm1-vegan-internet.grc
sudo gnuradio-companion gnuradio/VM2/vm2-vegan-internet.grc
```
