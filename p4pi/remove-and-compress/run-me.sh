#! /bin/bash

set -xe

echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6

sudo /etc/init.d/ntp stop

make clean
make
