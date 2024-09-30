## Middle Configuration

- pySX127x/ _(saved at /root/ folder)_
- P4edge-setup _(saved at /usr/sbin/p4edge-setup)_
 
### Configurations for *end device*

This file is meant to keep the network configurations we made in the Raspberry Pi, following the project description depicted in the README file. It has the output of the following commands:

1. ifconfig
2. ip route
3. route -n
4. iptables -nvL
5. iptables -t nat -nvL
6. ip netns exec ns ifconfig
7. ip netns exec ns ip route
8. ip netns exec ns route

## Inside main namespace

### ifconfig

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

### ip route

```
default via 10.30.0.129 dev int0 
10.0.0.0/24 dev wlan0 proto kernel scope link src 10.0.0.1 
10.10.0.0/24 dev bmv2-0 proto kernel scope link src 10.10.0.1 
10.30.0.0/24 dev int0 proto kernel scope link src 10.30.0.1
```

### route -n

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.30.0.129     0.0.0.0         UG    0      0        0 int0
10.0.0.0        0.0.0.0         255.255.255.0   U     0      0        0 wlan0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 bmv2-0
10.30.0.0       0.0.0.0         255.255.255.0   U     0      0        0 int0
```

### iptables -nvL

```
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
```

### iptables -t nat -nvL

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

### ip netns list

```
ns (id: 0)
```


## Inside ns namespace

### ip netns exec ns ifconfig

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

### ip netns exec ns ip route

```
default via 10.10.0.129 dev ns-bmv2-0 
10.0.0.0/24 via 10.30.0.1 dev ns-int0 
10.10.0.0/24 dev ns-bmv2-0 proto kernel scope link src 10.10.0.2 
10.30.0.0/24 dev ns-int0 proto kernel scope link src 10.30.0.129
```

### ip netns exec ns route

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.10.0.129     0.0.0.0         UG    0      0        0 ns-bmv2-0
10.0.0.0        10.30.0.1       255.255.255.0   UG    0      0        0 ns-int0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-bmv2-0
10.30.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-int0
```