# About the Power cases
The aim is to evaluate the performance and energy efficiency of a network setup comprising two Raspberry Pi devices equipped with LoRa modules. The focus is on measuring the latency, specifically the Round-Trip Time (RTT), and the power consumption across different components and communication interfaces within this network. 

![power.png](https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks/blob/main/Documentation/assets/power.png)

This diagram illustrates the layout of both Raspberry Pi devices and their respective interfaces, highlighting the key points where measurements will be taken.

## Aims
1. **Latency Calculation (Round-Trip Time - RTT):**
The aim is to calculate the round-trip time (RTT) for packets of varying sizes as they are transmitted between different points in the network architecture. This will help to understand the latency introduced by the network components and the LoRa communication.

- **Packet Sizes:** The sizes of the packets to be tested include: 64 bytes, 128 bytes, 256 bytes, 512 bytes, 1024 bytes, and 1500 bytes. These sizes cover a range of typical data packets used in network communications.

- **Measurement Points:**
    - **A ↔ F:** Measure the RTT between the Wi-Fi interface on Rasp-end and the Ethernet interface on Rasp-middle.
    - **B ↔ E:** Measure the RTT between the internal virtual interfaces within each Raspberry Pi.
    - **C ↔ D:** Measure the RTT across the LoRa communication link only.

2. **Power Consumption Analysis:**
The second major aim is to measure and analyze the power consumption of the network setup. Given the low-power nature of LoRa.

- **Components to Measure:**
    - **LoRa Modules (end and middle):** Measure the power consumption of the LoRa modules on both Raspberry Pi devices. This will include energy usage during packet transmission, reception, and idle states.
    - **Raspberry Pi Devices (end and middle):** Measure the overall power consumption of each Raspberry Pi, including the processing load from running scripts, and the communication interfaces (Wi-Fi, Ethernet, and LoRa).

## Ongoing tasks

- [X] Develop scripts for packet transmission and reception between Raspberry Pi devices - DONE

    - Script for end Raspberry Pi to handle packet sending, receiving ACKs, and calculating transmission times - DONE
    - Script for middle Raspberry Pi to handle packet forwarding, receiving packets, and sending ACKs - DONE

- [X] Measure and log the Round-Trip Time (RTT) for different packet sizes - DONE

    - 64 bytes, 128 bytes, 256 bytes, 512 bytes, 1024 bytes, and 1500 bytes - DONE

- [ ] Optimize transmission to reduce packet loss between Raspberry Pi devices - DOING

- [X] Integrate time stamping and TTL logging into the packet processing scripts - DONE

- [X] Analyze power consumption during different phases of packet transmission and reception - DOME

    - Measure power usage on LoRa modules during transmission, reception, and idle states - DOING
    - Measure overall power consumption of Raspberry Pi devices under different loads - DOING

- [ ] Implement error handling and packet retransmission logic to address packet loss issues - TODO

- [ ] Optimize LoRa communication parameters for better throughput and reliability - ?