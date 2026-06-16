# Troubleshooting

This document lists common issues that may happen while setting up and running the TCC experiment.

It covers problems related to:

* TAP interface setup
* GNU Radio Companion
* USRP/UHD detection
* BMv2 and p4c validation
* Basic network tests

## TAP Interface Already Exists

If `tap0` already exists and needs to be recreated, remove it first:

```bash
sudo ip link set dev tap0 down
sudo ip tuntap del dev tap0 mode tap
```

Then recreate it using the correct VM-specific configuration.

VM1:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.1/24
sudo ip link set dev tap0 up
```

VM2:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.2/24
sudo ip link set dev tap0 up
```

## Permission Denied When Using TAP

Make sure the TAP interface was created for the current Linux user:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
```

To confirm the current user:

```bash
echo $USER
```

If the TAP interface was created for the wrong user, remove it and create it again:

```bash
sudo ip link set dev tap0 down
sudo ip tuntap del dev tap0 mode tap
```

Then run the VM-specific TAP setup again.

## Validate TAP Configuration

Check whether `tap0` exists:

```bash
ip addr show tap0
```

Check whether the interface is up:

```bash
ip link show tap0
```

Expected IP addresses:

| Machine | Interface | IP Address         |
| ------- | --------- | ------------------ |
| VM1     | `tap0`    | `192.168.200.1/24` |
| VM2     | `tap0`    | `192.168.200.2/24` |

## GNU Radio Companion Does Not Open

Try opening GNU Radio Companion with:

```bash
sudo gnuradio-companion
```

If it still does not open, verify whether GNU Radio is installed:

```bash
gnuradio-companion --version
```

Also check whether the graphical environment is available, especially when using SSH.

## GNU Radio Flowgraph Does Not Run

Check the following points:

* the correct `.grc` file is open for each VM;
* the TAP block is configured to use `tap0`;
* the USRP parameters match the device being used;
* the TAP interface was created before running the flowgraph;
* both VM1 and VM2 flowgraphs are running.

Expected files:

```text
gnuradio/VM1/vm1-vegan-internet.grc
gnuradio/VM2/vm2-vegan-internet.grc
```

## USRP Not Detected

Run:

```bash
sudo uhd_find_devices
```

If no device is listed, check:

* whether the USRP is powered on;
* USB or Ethernet connection;
* host network configuration, for Ethernet-based USRPs;
* UHD installation;
* device permissions.

For Ethernet-based USRP devices, also check the network interfaces:

```bash
ip addr
```

## BMv2 Tools Not Found

Check whether `simple_switch` and `simple_switch_CLI` are installed:

```bash
which simple_switch
which simple_switch_CLI
```

Expected paths:

```text
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
```

If they are not found, rebuild and reinstall BMv2.

See:

```text
docs/setup/03-build-bmv2-behavioral-model.md
```

## p4c Tools Not Found

Check whether `p4c` and `p4c-bm2-ss` are installed:

```bash
which p4c
which p4c-bm2-ss
p4c --version
```

Expected version:

```text
p4c 1.2.3.0
```

If they are not found, rebuild and reinstall p4c.

See:

```text
docs/setup/04-build-p4c.md
```

## Ping Does Not Work

Run on VM1:

```bash
ping -I tap0 192.168.200.2
```

If the ping fails, check:

* `tap0` exists on both VMs;
* VM1 uses `192.168.200.1/24`;
* VM2 uses `192.168.200.2/24`;
* both GNU Radio flowgraphs are running;
* USRP devices are detected on both sides;
* the correct `.grc` file is running on each VM.

## iperf3 Does Not Connect

On VM1, start the server:

```bash
iperf3 -s
```

On VM2, run the client:

```bash
iperf3 -c 192.168.200.1 -t 60
```

If the connection fails, check:

* whether `iperf3 -s` is still running on VM1;
* whether VM2 can reach VM1 using `ping`;
* whether the GNU Radio flowgraphs are still running;
* whether `tap0` is up on both VMs.

## HTTP Tests Do Not Work

On VM1, start the HTTP server:

```bash
mkdir -p ~/data
echo "Hello, world - LoRa!" > ~/data/index.html
python3 -m http.server --directory ~/data 8080
```

On VM2, test with:

```bash
curl http://192.168.200.1:8080/
```

If the connection is refused, the HTTP server is probably not running or the wrong port is being used.

If the request hangs or times out, check:

* TAP configuration;
* GNU Radio flowgraphs;
* USRP detection;
* link stability;
* whether the VM1 server is still running.

## wget Download Is Too Slow or Fails

For file transfer tests, start the HTTP server on VM1 and download from VM2.

Example:

```bash
time wget http://192.168.200.1:8080/100kb.bin
```

If the download is too slow or fails, check:

* whether the file exists in `~/data`;
* whether the HTTP server is running on VM1;
* whether the GNU Radio flowgraphs are still running;
* whether the link is stable;
* whether the file size is appropriate for the experiment.

## siege Reports Failed Transactions

Small numbers of failed transactions may happen in constrained or unstable links.

Check:

* `availability`;
* `successful_transactions`;
* `failed_transactions`;
* `response_time`;
* `longest_transaction`.

For a basic validation, use a small load first:

```bash
siege http://192.168.200.1:8080/ -t60s -c5
```

Increase concurrency only after the basic test works reliably.

## Rebuild After Installation Issues

After installing BMv2 or p4c, update the linker cache:

```bash
sudo ldconfig
```

Then validate the tools again:

```bash
which simple_switch
which simple_switch_CLI
which p4c
which p4c-bm2-ss
```

## Recommended Debug Order

When something does not work, follow this order:

1. Check `tap0` on both VMs.
2. Check USRP detection with `sudo uhd_find_devices`.
3. Open the correct `.grc` file on each VM.
4. Run both GNU Radio flowgraphs.
5. Test with `ping`.
6. Test with `iperf3`.
7. Test with HTTP using `curl`.
8. Test file transfer using `wget`.
9. Run optional load tests using `siege`.
