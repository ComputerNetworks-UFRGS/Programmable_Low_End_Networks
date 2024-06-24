# Pilot Project [Prototype]

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

## Steps to build the prototype

### tasks finished
- [X] Learning and understanding P4
- [X] Learning how to use P4Pi OS to run P4 and how to configure virtual networks
- [X] Learning how to use LoRa technologies for our purposes
- [X] Learning scapy for packet processing
- [X] Building a simulation without the LoRa communication
      
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

### Ongoing tasks
- [ ] Figure out how to integrate LoRa Communication and P4Pi OS
    - probably using a dummy interface to receive and send packet from and to LoRa
- [ ] Rebuild sniffer script with scapy
- [ ] Rebuild sendp function to send packets to dummy interface

## Project Decisions
- Not implementing DHCP server on local network for ease of development

## Tasks for automating prototype execution (P4 side)
- [] Connect to wifi (Julien)
- [] ssh to p4pi (Julien)
- [] run the P4 code and check if it works (Marcelo)
- [] check internet connection (Marcelo)