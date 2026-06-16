# 03 - Running the GNU Radio Flowgraphs

The GNU Radio flowgraphs are separated by VM.

## Expected File Locations

```text
gnuradio/VM1/vm1-vegan-internet.grc
gnuradio/VM2/vm2-vegan-internet.grc
```

## VM1 Execution

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.1/24
sudo ip link set dev tap0 up
sudo uhd_find_devices
sudo gnuradio-companion gnuradio/VM1/vm1-vegan-internet.grc
```

Then click **Run** inside GNU Radio Companion.

## VM2 Execution

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.2/24
sudo ip link set dev tap0 up
sudo uhd_find_devices
sudo gnuradio-companion gnuradio/VM2/vm2-vegan-internet.grc
```

Then click **Run** inside GNU Radio Companion.

## Recommended Execution Order

1. Configure `tap0` on VM1.
2. Configure `tap0` on VM2.
3. Check USRP detection on both VMs.
4. Open the VM1 `.grc`.
5. Open the VM2 `.grc`.
6. Start both flowgraphs in GNU Radio Companion.
7. Run the tests in `docs/validation/02-basic-execution-tests.md`.
