#!/bin/bash
ROOT_USER=root
ROOT_PASS=raspberry
NAME_P4_MIDDLE=p4pi-middle
NAME_P4_END=p4pi-end
IP_P4_MIDDLE=192.168.4.2
IP_P4_END=192.168.4.1
INTERNET=8.8.8.8

sudo -i
${ADM_PASS}

#prerequisites
apt-get install sshpass

# !IMPORTANT: connect to p4pi-middle wifi access-point
#nmcli radio wifi
nmcli radio wifi on #activate the wifi device
#nmcli dev wifi list
nmcli dev wifi connect ${NAME_P4_MIDDLE} password ${ROOT_PASS}


# connect to p4pi-middle and run port-to-port.p4 code
sshpass -p ${ROOT_PASS} ssh ${ROOT_USER}${P4-MIDDLE}
    cd /
    sudo ./port-to-port.p4


# check if the code is running correctly (optional)

# !IMPORTANT: connect to p4pi-end wifi access-point

sudo -i
${ADM_PASS}
nmcli radio wifi on
nmcli dev wifi connect ${NAME_P4_END} password ${ROOT_PASS}

# connect to p4pi-end and check if there is internet access
sshpass -p ${ROOT_PASS} ssh ${ROOT_USER}${P4_END}
    ping ${INTERNET}

# run setup_eth_wlan_bridhe.sh on p4pi-end
    ./setup_eth_wlan_bridge.sh

# check if internet access is granted on wlan0
    ping ${INTERNET}