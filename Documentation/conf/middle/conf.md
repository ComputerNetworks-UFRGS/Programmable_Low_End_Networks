## Middle Configuration

- pySX127x/ _(saved at /root/ folder)_
- P4edge-setup _(saved at /usr/sbin/p4edge-setup)_

### Configurations for *middle device*

This file is meant to keep the network configurations we made in the Raspberry Pi, following the project description depicted in the README file. It has the output of the following commands:

1. ifconfig
2. ip route
3. route -n
4. iptables -nvL
5. iptables -t nat -nvL
6. ip netns exec ns ifconfig
7. ip netns exec ns ip route
8. ip netns exec ns route

### ifconfig

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


### route -n

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

### iptables -nvL

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

### iptables -t nat -nvL

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

## Inside ns namespace

### ip netns exec ns ifconfig

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

### ip netns exec ns ip route

```
default via 10.20.0.1 dev ns-int0 
10.0.0.0/24 via 10.10.0.1 dev ns-bmv2-0 
10.10.0.0/24 dev ns-bmv2-0 proto kernel scope link src 10.10.0.129 
10.20.0.0/24 dev ns-int0 proto kernel scope link src 10.20.0.129 
10.30.0.0/24 via 10.10.0.1 dev ns-bmv2-0 
```

### ip netns exec ns route

```
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         10.20.0.1       0.0.0.0         UG    0      0        0 ns-int0
10.0.0.0        10.10.0.1       255.255.255.0   UG    0      0        0 ns-bmv2-0
10.10.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-bmv2-0
10.20.0.0       0.0.0.0         255.255.255.0   U     0      0        0 ns-int0
10.30.0.0       10.10.0.1       255.255.255.0   UG    0      0        0 ns-bmv2-0
```