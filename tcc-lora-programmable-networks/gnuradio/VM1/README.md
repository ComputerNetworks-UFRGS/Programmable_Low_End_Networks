# VM1 GNU Radio Flowgraph

Add the VM1 GNU Radio flowgraph in this folder.

Recommended file name:

```text
vm1-vegan-internet.grc
```

## VM1 TAP Configuration

VM1 uses:

```text
tap0 -> 192.168.200.1/24
```

Setup:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.1/24
sudo ip link set dev tap0 up
```

## Run VM1 Flowgraph

From the project root:

```bash
sudo gnuradio-companion gnuradio/VM1/vm1-vegan-internet.grc
```

Then click **Run** inside GNU Radio Companion.
