# Instructions on how to run the research prototype

## P4Pi configurations

### p4pi-middle
    1. Enable BMV2 backend
    2. Connect ethernet-USB adapter
    3. Configure switch ports on /usr/bin/bmv2-start
        - port 0 to eth0
        - port 1 to ethernet adapter
    4. Run port-to-port P4 program

### p4pi-end
    1. Connect ethernet with internet access
    2. Run setup_eth_wlan_bridge

## LoRa configurations