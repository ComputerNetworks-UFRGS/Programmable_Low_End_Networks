#!/bin/bash

echo "Redirecting veth1 end-point"
ip netns exec gigport ip link set veth1-1 netns 1
ip link set dev veth1-1 up
brctl addbr br2
brctl setageing br2 0
ip link set dev br2 up

echo "Connecting eth0 to br2"
ip link set eth0 promisc on
brctl addif br2 eth0
brctl addif br2 veth1-1

echo "Defining IPs"
ip addr add 192.168.15.20/24 dev br2
ip addr add 192.168.15.21/24 dev br0

ifconfig eth0 0.0.0.0 up
ip addr add 192.168.15.22/24 dev eth0

