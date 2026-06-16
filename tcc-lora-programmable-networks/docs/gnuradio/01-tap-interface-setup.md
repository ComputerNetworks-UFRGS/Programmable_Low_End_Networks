# 01 - TAP Interface Setup

The TAP interface must be configured before running the GNU Radio flowgraphs.

This experiment uses one TAP interface named `tap0` on each virtual machine.

## Network Configuration

| Machine | Interface | IP Address         |
| ------- | --------- | ------------------ |
| VM1     | `tap0`    | `192.168.200.1/24` |
| VM2     | `tap0`    | `192.168.200.2/24` |

## VM1 Setup

Run the following commands on VM1:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.1/24
sudo ip link set dev tap0 up
```

## VM2 Setup

Run the following commands on VM2:

```bash
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip addr add dev tap0 192.168.200.2/24
sudo ip link set dev tap0 up
```

## Validate the TAP Interface

After configuring `tap0`, validate the interface on each VM:

```bash
ip addr show tap0
```

Expected result:

* VM1 should show `192.168.200.1/24`
* VM2 should show `192.168.200.2/24`

Also check whether the interface is up:

```bash
ip link show tap0
```

The interface should appear with `UP` in the output.

## Recreate the TAP Interface

If `tap0` already exists and needs to be recreated, remove it first:

```bash
sudo ip link set dev tap0 down
sudo ip tuntap del dev tap0 mode tap
```

Then run the VM-specific setup commands again.

## Notes

* The TAP interface must be created before running the GNU Radio flowgraph.
* The same interface name, `tap0`, is used on both VMs.
* VM1 and VM2 must use different IP addresses.
* The `$USER` variable assigns the TAP interface to the current Linux user.
