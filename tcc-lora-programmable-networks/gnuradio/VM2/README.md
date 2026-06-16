# VM2 GNU Radio Flowgraph

Add the VM2 GNU Radio flowgraph in this folder.

Recommended file name:

```text
vm2-vegan-internet.grc
```

## VM2 TAP Configuration

VM2 uses:

```text
tap0 -> 192.168.200.2/24
```

Setup:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.2/24
sudo ip link set dev tap0 up
```

## Run VM2 Flowgraph

From the project root:

```bash
sudo gnuradio-companion gnuradio/VM2/vm2-vegan-internet.grc
```

Then click **Run** inside GNU Radio Companion.
