#!/bin/bash

# ---------------------------------------
# script executado automaticamente ao
# iniciar P4Pi
# ---------------------------------------

# cria bridge br0
brctl addbr br0
ip netns add gigport

# cria bridge br1 dentro do p4pi
ip netns exec gigport brctl addbr br1
ip netns exec gigport brctl setageing br1 0

brctl setageing br0 0

# cria peer para veth's
ip link add dev veth0 type veth peer name veth0-1
ip link add dev veth1 type veth peer name veth1-1

# set up
ip link set dev veth0 up
ip link set dev veth1 up

ip link set dev veth0-1 up
ip link set veth1-1 netns gigport
ip netns exec gigport ip link set dev veth1-1 up
ip netns exec gigport ethtool -K veth1-1 tx off

# recurso de alívio de congestionamento que funciona 
# fornecendo controle de fluxo de nível de enlace 
# para todo o tráfego em um enlace Ethernet totalmente duplex
ethtool -K veth0 tx off
ethtool -K veth1 tx off

ethtool -K veth0-1 tx off

# conecta br0 e veth0-1
brctl addif br0 veth0-1
# conecta br1 e veth1-1

ip netns exec gigport brctl addif br1 veth1-1
ip netns exec gigport ip addr add 192.168.4.150/24 dev br1
ip netns exec gigport ip link set dev br1 up