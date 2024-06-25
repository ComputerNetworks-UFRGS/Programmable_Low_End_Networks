#!/bin/bash

ROOT_USER=root
ROOT_PASS=raspberry
SSID_P4_MIDDLE=p4pi-middle
SSID_P4_END=p4pi-end
IP_P4_MIDDLE=192.168.4.2
IP_P4_END=192.168.4.1
INTERNET=http://google.com
online=1

function is_online() {
    # -q : Silence mode
    # --spider : don't get, just check page availability
    # $? : shell return code
    # 0 : shell "All OK" code
    wget -q --spider ${INTERNET}

    # echoes return code
    echo $?
}

function run_p4() {
    # creates dir on specified location and moves file
    # TODO: CORRIGIR CRIAÇAO DA PASTA COM NOME CROPPADO
    # mkdir "~/bmv2/examples/${$1%.*}"
    cp $1 "~/bmv2/examples/$1/"

    # runs the p4-code following p4pi pipeline
    echo "Running $1 on bmv2 switch"
    echo "$1" > t4p4s-switch
    echo "Restarting bmv2.service"
    systemctl restart bmv2.service
    
    # waits for the p4 to compile (p4pi does this for us)
    sleep 2

    if [ systemctl is-active --quiet "bmv2.service" ]; then
        echo "bmv2 is running successfully!"
    else
        echo "Something went wrong!"
        return 1
    fi

    return 0
}

# !IMPORTANT: connect to p4pi-middle wifi access-point
function connect_to_wifi(){
    local ssid="$1"
    local password="$2"
    nmcli radio wifi on #activate the wifi device
    nmcli dev wifi connect $ssid password $password
    if [ $? -ne 0 ]; then
        echo "Failed to connect to WiFi access point: $ssid"
        exit 1
    else
        echo "Connected to WiFi access point: $ssid"
    fi
}

#Check if we are in root
if [ "$(id -u)" -ne 0 ]; then
    echo "You need to be in root to launch the entire script" >&2
    exit 1
fi

#prerequisites
apt-get install sshpass


# connect to p4pi-middle and run port-to-port.p4 code
connect_to_wifi "$SSID_P4_MIDDLE" "$ROOT_PASS"
sshpass -p "${ROOT_PASS}" ssh "${ROOT_USER}@${IP_P4_MIDDLE}" << EOF
    run_p4 "port-to-port.p4"
EOF

# check if the code is running correctly (optional)
sshpass -p "${ROOT_PASS}" ssh "${ROOT_USER}@${IP_P4_MIDDLE}" << EOF
    pgrep -f port-to-port.p4 > /dev/null
    if [ \$? -eq 0 ]; 
    then
        echo "port-to-port.p4 is running."
    else
        echo "port-to-port.p4 is not running."
        exit 1
    fi
EOF

# !IMPORTANT: connect to p4pi-end wifi access-point
nmcli radio wifi on
nmcli dev wifi connect ${NAME_P4_END} password ${ROOT_PASS}

# connect to p4pi-end and check if there is internet access
connect_to_wifi "$SSID_P4_END" "$ROOT_PASS"
sshpass -p "${ROOT_PASS}" ssh "${ROOT_USER}@${P4_END}" << EOF
    ping ${INTERNET}

# run setup_eth_wlan_bridhe.sh on p4pi-end
    ./setup_eth_wlan_bridge.sh
EOF

# check if internet access is granted on wlan0
    if [ $(is_online) -eq 0 ]; then
        echo "Online"
    else
        echo "Offline"
    fi
