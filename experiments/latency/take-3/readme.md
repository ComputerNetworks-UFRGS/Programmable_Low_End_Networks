# Take 3

The sized of the packets are:
1. 64B
2. 128B
3. 255B

This is the **full size**, taking in account the IPV4 and Ethernet headers.

We made **35 repetitions** on every ping test.

## Interfaces used

1. A ↔ F <br/>
    int0 ↔ int0
2. B ↔ E <br/>
    ns-bmv2-0 ↔ ns-bmv2-0
3. C ↔ D <br/>
    ns-bmv2-0 ↔ ns-bmv2-0
    
    (here we are using the `test-cd-latency.py` script that makes measurements that can be used to calculate exactly how much time it took from interface to interface, which means that we start the counter when we "sniff" the packet on the respective socket and we stop the counter when we send the response to the respective socket on the end device).


## Commands used

```bash
# ------------------------------------------
# ------------------- AF -------------------
# ------------------------------------------

# AF - no compression
ping -I int0 -s 22 -c 35 143.54.48.17 > AF-64B-no-compression.txt
ping -I int0 -s 86 -c 35 143.54.48.17 > AF-128B-no-compression.txt
fping -I int0 -b 212 -p 2300 -c 35 143.54.48.17 > AF-255B-no-compression.txt

# AF - compression
fping -I int0 -b 22 -c 35 143.54.48.17 > AF-64B-compression.txt
fping -I int0 -b 86 -c 35 143.54.48.17 > AF-128B-compression.txt
fping -I int0 -b 212 -c 35 143.54.48.17 > AF-255B-compression.txt

# ------------------------------------------
# ------------------- BE -------------------
# ------------------------------------------

# BE - no compression
ip netns exec ns ping -I ns-bmv2-0 -c 35 -s 22 10.10.0.129 > BE-64B-no-compression.txt
ip netns exec ns ping -I ns-bmv2-0 -c 35 -s 86 10.10.0.129 > BE-128B-no-compression.txt
ip netns exec ns fping -I ns-bmv2-0 -c 35 -b 212 -p 2300 10.10.0.129 > BE-255B-no-compression.txt

# BE - compression
ip netns exec ns fping -I ns-bmv2-0 -c 35 -b 22 10.10.0.129 > BE-64B-compression.txt
ip netns exec ns fping -I ns-bmv2-0 -c 35 -b 86 10.10.0.129 > BE-128B-compression.txt
ip netns exec ns fping -I ns-bmv2-0 -c 35 -b 212 10.10.0.129 > BE-255B-compression.txt

# ------------------------------------------
# ------------------- CD -------------------
# ------------------------------------------

# CD - no compression
ip netns exec ns fping -c 35 -I ns-bmv2-0 -p 700 -b 22 10.10.0.129 > CD-64B-no-compression.txt
ip netns exec ns fping -c 35 -I ns-bmv2-0 -p 1000 -b 86 10.10.0.129 > CD-128B-no-compression.txt
ip netns exec ns fping -c 35 -I ns-bmv2-0 -p 2300 -b 212 10.10.0.129 > CD-255B-no-compression.txt

# CD - compression
ip netns exec ns fping -c 35 -I ns-bmv2-0 -b 22 10.10.0.129 > CD-64B-compression.txt
ip netns exec ns fping -c 35 -I ns-bmv2-0 -b 86 10.10.0.129 > CD-128B-compression.txt
ip netns exec ns fping -c 35 -I ns-bmv2-0 -p 500 -b 212 10.10.0.129 > CD-255B-compression.txt

```

## Calculations

To calculate CD, take END_TIME - MIDDLE_TIME (total time - time between Middle LoRa script and BMV2).
To calculate DE, take END_TIME + MIDDLE_TIME (Mayer write and read latencies).
