sudo ip link set dev $1 down
sudo ip link set dev $1 name eth1
sudo ip link set dev eth1 up

