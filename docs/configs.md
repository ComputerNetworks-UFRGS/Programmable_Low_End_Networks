# Raspberry Pi Setup Scripts

This describes the scripts we configure to run in boot on every device to configure the network we designed, described below:

\*\* The firewall was used to optimize the network communication, dropping all unecessary traffic. For more details about the firewall, please check out the [Firewall settings](/firewall.md) docs page.

![Network designed](/assets/setup/network-PLEN.png)

## End device configuration

-   pySX127x/ _(saved at /root/ folder)_
-   P4edge-setup _(saved at /usr/sbin/p4edge-setup)_

### Configurations for _end device_

This file is meant to keep the network configurations we made in the Raspberry Pi, following the project description depicted in the README file. It has the output of the following commands:

1. ifconfig
2. ip route
3. route -n
4. iptables -nvL
5. iptables -t nat -nvL
6. ip netns exec ns ifconfig
7. ip netns exec ns ip route
8. ip netns exec ns route

### $ ifconfig

```
bmv2-0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.0.1  netmask 255.255.255.0  broadcast 10.10.0.255
        ether ce:b3:fc:9f:cb:cb  txqueuelen 1000  (Ethernet)

int0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.30.0.1  netmask 255.255.255.0  broadcast 10.30.0.255
        ether d4:d8:53:f6:32:cc  txqueuelen 1000  (Ethernet)

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)

lorarecv: flags=195<UP,BROADCAST,RUNNING,NOARP>  mtu 1500
        ether 36:16:95:46:ed:2d  txqueuelen 1000  (Ethernet)

lorasend: flags=195<UP,BROADCAST,RUNNING,NOARP>  mtu 1500
        ether 96:cd:02:c7:d3:36  txqueuelen 1000  (Ethernet)

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.0.1  netmask 255.255.255.0  broadcast 10.0.0.255
        ether d8:3a:dd:88:ca:0a  txqueuelen 1000  (Ethernet)

```

### $ ip route

```
default via 10.30.0.129 dev int0
10.0.0.0/24 dev wlan0 proto kernel scope link src 10.0.0.1
10.10.0.0/24 dev bmv2-0 proto kernel scope link src 10.10.0.1
10.30.0.0/24 dev int0 proto kernel scope link src 10.30.0.1
```

### $ route -n

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.30.0.129     0.0.0.0         UG    0      0        0 int0
10.0.0.0        0.0.0.0         255.255.255.0   U     0      0        0 wlan0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 bmv2-0
10.30.0.0       0.0.0.0         255.255.255.0   U     0      0        0 int0
```

### $ iptables -nvL

```
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
```

### $ iptables -t nat -nvL

```
Chain PREROUTING (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain POSTROUTING (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
```

### $ ip netns list

```
ns (id: 0)
```

## End ns namespace

### $ ip netns exec ns ifconfig

```
ns-bmv2-0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.0.2  netmask 255.255.255.0  broadcast 10.10.0.255
        inet6 fe80::9862:78ff:fe74:fe65  prefixlen 64  scopeid 0x20<link>
        ether 9a:62:78:74:fe:65  txqueuelen 1000  (Ethernet)
        RX packets 11  bytes 1076 (1.0 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8861  bytes 878469 (857.8 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

ns-int0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.30.0.129  netmask 255.255.255.0  broadcast 10.30.0.255
        inet6 fe80::8b5:a3ff:fe50:b9f6  prefixlen 64  scopeid 0x20<link>
        ether 0a:b5:a3:50:b9:f6  txqueuelen 1000  (Ethernet)
        RX packets 8895  bytes 880023 (859.3 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 51  bytes 2630 (2.5 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

### $ ip netns exec ns ip route

```
default via 10.10.0.129 dev ns-bmv2-0
10.0.0.0/24 via 10.30.0.1 dev ns-int0
10.10.0.0/24 dev ns-bmv2-0 proto kernel scope link src 10.10.0.2
10.30.0.0/24 dev ns-int0 proto kernel scope link src 10.30.0.129
```

### $ ip netns exec ns route

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.10.0.129     0.0.0.0         UG    0      0        0 ns-bmv2-0
10.0.0.0        10.30.0.1       255.255.255.0   UG    0      0        0 ns-int0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-bmv2-0
10.30.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-int0
```

### Setup script _/usr/sbin/p4edge-setup_

```bash
#!/bin/bash
set -x

echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1 > /proc/sys/net/ipv4/ip_forward

# creates and defines IP for dummy interfaces
ip link add lorasend type dummy
ip link add lorarecv type dummy
ip link set lorasend up
ip link set lorarecv up

# create veth pairs for bmv2 and internet

ip link add bmv2-0 type veth peer name ns-bmv2-0
ip link add int0 type veth peer name ns-int0

# create namespace and assign peers from veth pairs to ns

ip netns add ns
ip link set ns-bmv2-0 netns ns
ip link set ns-int0 netns ns

# init ip addresses for veth pairs

#  ----> veth pair bmv2

ip addr add 10.10.0.128/24 broadcast 10.10.0.255 dev bmv2-0
ip link set bmv2-0 up

ip netns exec ns ip link set dev ns-bmv2-0 address ea:89:b7:c2:bb:35
ip netns exec ns ip addr add 10.10.0.129/24 broadcast 10.10.0.255 dev ns-bmv2-0
ip netns exec ns ip link set ns-bmv2-0 up

#  ----> veth pair int0

ip addr add 10.20.0.1/24 broadcast 10.20.0.255 dev int0
ip link set int0 up

ip netns exec ns ip addr add 10.20.0.129/24 broadcast 10.20.0.255 dev ns-int0
ip netns exec ns ip link set ns-int0 up

# init routes

#  ----> routes inside namespace

ip netns exec ns ip route add 10.30.0.0/24 via 10.10.0.1 dev ns-bmv2-0 # DNS
ip netns exec ns ip route add 10.0.0.0/24 via 10.10.0.1 dev ns-bmv2-0 # Devices
ip netns exec ns ip route add default via 10.20.0.1 dev ns-int0

#  ----> local host routes

ip route add 10.30.0.0/24 via 10.20.0.129 dev int0 # DNS
ip route add 10.0.0.0/24 via 10.20.0.129 dev int0 # Devices

# init local interfaces

networkctl up eth0 ; dhclient eth0
ip link set wlan0 down
ip netns exec ns arp -s 10.10.0.1 9a:62:78:74:fe:65

# starts the bmv2 switch
systemctl stop t4p4s-switch
echo 'three-ports' > /root/t4p4s-switch

ip link set wlan0 down

systemctl restart ssh.service
systemctl restart bmv2.service
```

<hl>

## Middle device configuration

-   pySX127x/ _(saved at /root/ folder)_
-   P4edge-setup _(saved at /usr/sbin/p4edge-setup)_

### Configurations for _middle device_

This file is meant to keep the network configurations we made in the Raspberry Pi, following the project description depicted in the README file. It has the output of the following commands:

1. ifconfig
2. ip route
3. route -n
4. iptables -nvL
5. iptables -t nat -nvL
6. ip netns exec ns ifconfig
7. ip netns exec ns ip route
8. ip netns exec ns route

### $ ifconfig

```
bmv2-0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.0.128  netmask 255.255.255.0  broadcast 10.10.0.255
        ether ee:c7:b4:4a:14:3e  txqueuelen 1000  (Ethernet)

eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 143.54.49.51  netmask 255.255.252.0  broadcast 143.54.51.255
        ether d8:3a:dd:88:ca:94  txqueuelen 1000  (Ethernet)

int0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.20.0.1  netmask 255.255.255.0  broadcast 10.20.0.255
        ether 22:10:5a:72:7e:01  txqueuelen 1000  (Ethernet)

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)

lorarecv: flags=195<UP,BROADCAST,RUNNING,NOARP>  mtu 1500
        ether 5a:39:6d:6b:13:62  txqueuelen 1000  (Ethernet)

lorasend: flags=195<UP,BROADCAST,RUNNING,NOARP>  mtu 1500
        ether 7a:4e:0f:76:fc:6a  txqueuelen 1000  (Ethernet)
```

### $ route -n

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         143.54.48.1     0.0.0.0         UG    0      0        0 eth0
10.0.0.0        10.20.0.129     255.255.255.0   UG    0      0        0 int0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 bmv2-0
10.20.0.0       0.0.0.0         255.255.255.0   U     0      0        0 int0
10.30.0.0       10.20.0.129     255.255.255.0   UG    0      0        0 int0
143.54.48.0     0.0.0.0         255.255.252.0   U     0      0        0 eth0
```

### $ iptables -nvL

```
Chain INPUT (policy ACCEPT 107K packets, 20M bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy ACCEPT 558 packets, 73602 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 ACCEPT     all  --  eth0   br0     0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
    0     0 ACCEPT     all  --  br0    eth0    0.0.0.0/0            0.0.0.0/0

Chain OUTPUT (policy ACCEPT 30663 packets, 6754K bytes)
 pkts bytes target     prot opt in     out     source               destination
```

### $ iptables -t nat -nvL

```
Chain PREROUTING (policy ACCEPT 6159 packets, 1221K bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain INPUT (policy ACCEPT 6139 packets, 1218K bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 25 packets, 1676 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain POSTROUTING (policy ACCEPT 7 packets, 467 bytes)
 pkts bytes target     prot opt in     out     source               destination
   34  3872 MASQUERADE  all  --  *      eth0    0.0.0.0/0            0.0.0.0/0
    0     0 MASQUERADE  all  --  *      br0     0.0.0.0/0            0.0.0.0/0
    0     0 MASQUERADE  all  --  *      wlan0   0.0.0.0/0            0.0.0.0/0
    0     0 MASQUERADE  all  --  *      eth0    0.0.0.0/0            0.0.0.0/0
```

## Middle ns namespace

### $ ip netns exec ns ifconfig

```
ns-bmv2-0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.0.129  netmask 255.255.255.0  broadcast 10.10.0.255
        inet6 fe80::e889:b7ff:fec2:bb35  prefixlen 64  scopeid 0x20<link>
        ether ea:89:b7:c2:bb:35  txqueuelen 1000  (Ethernet)
        RX packets 11  bytes 1115 (1.0 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 15  bytes 1146 (1.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

ns-int0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.20.0.129  netmask 255.255.255.0  broadcast 10.20.0.255
        inet6 fe80::2ca8:4ff:fe0c:5a3e  prefixlen 64  scopeid 0x20<link>
        ether 2e:a8:04:0c:5a:3e  txqueuelen 1000  (Ethernet)
        RX packets 11  bytes 1103 (1.0 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 15  bytes 1146 (1.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```

### $ ip netns exec ns ip route

```
default via 10.20.0.1 dev ns-int0
10.0.0.0/24 via 10.10.0.1 dev ns-bmv2-0
10.10.0.0/24 dev ns-bmv2-0 proto kernel scope link src 10.10.0.129
10.20.0.0/24 dev ns-int0 proto kernel scope link src 10.20.0.129
10.30.0.0/24 via 10.10.0.1 dev ns-bmv2-0
```

### $ ip netns exec ns route

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.20.0.1       0.0.0.0         UG    0      0        0 ns-int0
10.0.0.0        10.10.0.1       255.255.255.0   UG    0      0        0 ns-bmv2-0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-bmv2-0
10.20.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-int0
10.30.0.0       10.10.0.1       255.255.255.0   UG    0      0        0 ns-bmv2-0
```

### Setup script _/usr/sbin/p4edge-setup_

```bash
#!/bin/bash
set -x

echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1 > /proc/sys/net/ipv4/ip_forward

# creates and defines IP for dummy interfaces
ip link add lorasend type dummy
ip link add lorarecv type dummy
ip link set lorasend up
ip link set lorarecv up

# create veth pairs for bmv2 and internet

ip link add bmv2-0 type veth peer name ns-bmv2-0
ip link add int0 type veth peer name ns-int0

# create namespace and assign peers from veth pairs to ns

ip netns add ns
ip link set ns-bmv2-0 netns ns
ip link set ns-int0 netns ns

# init ip addresses for veth pairs

#  ----> veth pair bmv2

ip addr add 10.10.0.1/24 broadcast 10.10.0.255 dev bmv2-0
ip link set bmv2-0 up

ip netns exec ns ip link set dev ns-bmv2-0 address 9a:62:78:74:fe:65
ip netns exec ns ip addr add 10.10.0.2/24 broadcast 10.10.0.255 dev ns-bmv2-0
ip netns exec ns ip link set ns-bmv2-0 up

#  ----> veth pair int0

ip addr add 10.30.0.1/24 broadcast 10.30.0.255 dev int0
ip link set int0 up
ip link set dev int0 address d4:d8:53:f6:32:cc

ip netns exec ns ip addr add 10.30.0.129/24 broadcast 10.30.0.255 dev ns-int0
ip netns exec ns ip link set ns-int0 up

# init routes

#  ----> routes inside namespace

ip netns exec ns ip route add default via 10.10.0.129 dev ns-bmv2-0
ip netns exec ns ip route add 10.0.0.0/24 via 10.30.0.1 dev ns-int0

#  ----> local host routes

ip route add default via 10.30.0.129 dev int0

# init local interfaces

ip addr add 10.0.0.1/24 broadcast 10.0.0.255 dev wlan0
ip link set eth0 down

ip netns exec ns arp -s 10.10.0.129 ea:89:b7:c2:bb:35

#hardware calculating chksum for bind9 not working. Forcing software to do it
ethtool -K int0 rx off tx off

#Log file for bind9

mkdir /var/log/bind
chown bind:bind /var/log/bind

# starts the bmv2 switch
systemctl stop t4p4s-switch
echo 'three-ports' > /root/t4p4s-switch

systemctl restart bmv2.service
systemctl restart udhcpd.service
systemctl restart ssh.service
systemctl restart bind9.service
```
