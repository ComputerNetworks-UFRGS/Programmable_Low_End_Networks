# Programmable_Low_End_Networks
UFRGS - Low End Networks project repository.

## Pilot Project [Prototype]

In this document, we aim to explain what is the prototype we are developing; the tasks we already made and the ones that are to come.

![prototype](https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks/assets/103913045/d92c94cd-479a-4a5c-883f-a585edb2414b)
_The image above describes the structure of the prototype we are building._

<br/>

To build the network described above, we have to develop 2 important parts:

1. The communication through the [BMV2 software switch](https://github.com/p4lang/behavioral-model) using [P4](https://github.com/p4lang) on the [P4Pi OS](https://github.com/p4lang/p4pi).
2. The [LoRa SX127x](https://www.dragino.com/products/lora/item/106-lora-gps-hat.html) antennas communication using [scapy](https://scapy.net/) and some LoRa base codes.

The idea is that the communication with the network will occur passing through the programmable switch, and then, through the LoRa Radio transmissions, giving us the power to communicate over long distances. The speed of the radio link will be slow (something along the line of 400bps to 50Kbps), however, it will be enough to demonstrate the idea and make some experiments.
<br/>

We developed these parts separately, and so, now we have to merge these two technologies together.

<br/>

## Steps to integrate project parts
      
### merging projects
- [X] configure GPIO pins for LoRa
- [X] configure SPI on Raspberry Pi

    [link to the issue](https://github.com/mayeranalytics/pySX127x/issues/21) - Comment by Mike Routen made on Dec 5, 2018

    Enable SPI on Interface Options
    ```console
        sudo raspi-config
    ```

    1. "dtoverlay=spi0-cs,cs0_pin=25" at the end of `/boot/config.txt`
    2. clone the repo [pySX127x](https://github.com/mayeranalytics/pySX127x)
    3. Follow installation process
    4. Change the values described on the github Issue in SX127x/board_config
    5. Add the respective lines found on the github Issue to SX127x/constants.py
    6. Add the respective lines found on the github Issue to SX127x/LoRa.py
    7. Try and run sudo ./lora_util.py
        1. Assertion Error: Try and reboot the raspberry

## Project Decisions
- Not implementing DHCP server on local network for ease of development

## Ongoing tasks
- [X] Figure out best way to integrate LoRa Communication and P4Pi OS - DOING
    - usage of dummy interfaces
    - switch with 3 ports (one to communicate with clients, one to send to LoRa and one to receive from LoRa)
- [ ] Find a better transmission solution between the 2 raspberry pi to avoid packet loss (Julien) - DOING
- [X] Test 3 ports approach
- [X] Configure virtual network on startup (Julien) - DONE
- [X] Rebuild sniffer script with scapy
    - sniffer for DHCP packets as test 
- [X] Decode packets received on the middle p4pi - DONE
- [X] Forward packets to the network - DONE
- [ ] Analyse throughput of LoRa Antenas - DOING
- [X] Build filter for only client packets, ignoring other packets on the sniffers - DONE (basic version)

## Archive
- [ ] Build script to configure virtual network for switch with 3 ports
    - Connect to wifi (Julien) - DONE
    - ssh to p4pi (Julien) - DONE
    - run the P4 code and check if it works (Marcelo) - DOING
    - check internet connection (Marcelo) - DONE

## Future Tasks
- [ ] Implement DHCP and NAT on local Pi network
- [ ] Run the LTP protocol P4 code on P4Pi
- [ ] Implement packets filter on P4


# About the Power cases
The aim is to calculate how much time takes the packet to be transmitted depending on the size of the packet.
![power.png](https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks/blob/main/Documentation/assets/power.png)

The image above describes the both raspberry pi with their architectures.

## Aims
1. Latency Calculation (Round-Trip Time - RTT):
The aim is to calculate the round-trip time (RTT) for packets of varying sizes as they are transmitted between different points in the network architecture. This will help to understand the latency introduced by the network components and the LoRa communication.

- Packet Sizes: The sizes of the packets to be tested include: 64 bytes, 128 bytes, 256 bytes, 512 bytes, 1024 bytes, and 1500 bytes. These sizes cover a range of typical data packets used in network communications.

- Measurement Points:
    - A ↔ F: Measure the RTT between the Wi-Fi interface on Rasp-end and the Ethernet interface on Rasp-middle.
    - B ↔ E: Measure the RTT between the internal virtual interfaces within each Raspberry Pi.
    - C ↔ D: Measure the RTT across the LoRa communication link only.

2. Power Consumption Analysis:
The second major aim is to measure and analyze the power consumption of the network setup. Given the low-power nature of LoRa.

- Components to Measure:
    - LoRa Modules (end and middle): Measure the power consumption of the LoRa modules on both Raspberry Pi devices. This will include energy usage during packet transmission, reception, and idle states.
    - Raspberry Pi Devices (end and middle): Measure the overall power consumption of each Raspberry Pi, including the processing load from running scripts, and the communication interfaces (Wi-Fi, Ethernet, and LoRa).