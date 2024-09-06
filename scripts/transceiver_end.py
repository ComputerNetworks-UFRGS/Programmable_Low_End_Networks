#!/usr/bin/env python3

import sys, threading, argparse
from time import time,sleep
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD
from socket import *

BOARD.setup()
verbose = False

TREDBOLD =  '\033[31;1m'
TGREEN =  '\033[32m' 
TYELLOW =  '\033[33m'

class Queue:
    def __init__(self):
        self.items = []
        self.block = False

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        if not self.block:
            print(self.size())
            self.items.insert(0,item)
            self.block = self.size() > 200
        else:
            self.block = not self.isEmpty()


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
            packet.summary()
            if host == 'end':
                known_ip = packet[IP].src in [pos[0] for pos in self.list]
            else:
                known_ip = (packet[IP].src in self.list) and (packet[IP].src != "143.54.49.51")

            if known_ip:
                # the packet is converted into bytes and added to the queue
                self.pktlist.enqueue(bytes(packet))
                print(TYELLOW + "SEND: ")
                # print(packet.summary())
                print(packet.summary())
            else:
                if packet.haslayer(BOOTP):
                    if host == "end":
                        #self.pktlist.enqueue(bytes(packet))
                        if (packet[BOOTP].yiaddr != '0.0.0.0' and (packet[BOOTP].yiaddr not in [pos[0] for pos in self.list])):
                            self.list.append((packet[BOOTP].yiaddr, packet[Ether].dst))
                            if verbose:
                                print(self.list)
                                print(f"IP {packet[BOOTP].yiaddr}" )

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
        #self.sock = socket(AF_INET, SOCK_DGRAM)
        #self.sock.bind( ("0.0.0.0", 3001) )

        if host == "end":
            self.OWN_IP = get_if_addr("wlan0")
            self.OWN_MAC = get_if_hwaddr("wlan0")
        else:
            self.OWN_IP = get_if_addr("eth0")
            self.OWN_MAC = get_if_hwaddr("eth0")

        if host == "middle":
            p = srp1(Ether(dst = "ff:ff:ff:ff:ff:ff")/IP(dst="8.8.8.8", ttl = 1)/ICMP()/"XXXXXXXXXXX")
            self.RMAC = p[Ether].src


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

                print(TGREEN + "Packet in!  " + packet.summary())

                # if it's not a DHCP packet
                if packet.haslayer(IP) and (not packet.haslayer(BOOTP)):
                    if host == "end":
                        #if packet.haslayer(DNS):
                        #    a = Ether(src="00:00:00:00:00:00",dst="00:00:00:00:00:00")/IP(src="127.0.0.1",dst="127.0.0.1")/UDP(sport=RandShort(),dport=3001)/DNS( id = packet[DNS].id, qr=1, aa=1, qdcount=1, ancount=1, qd=packet[DNS].qd, an=packet[DNS].an)
                         #   a.show()
                         #   self.sock.sendto(bytes(a), addr)
                         #   #del packet[1].chksum
                            #del packet[2].chksum
                            #packet.show2()
                        #else:
                        for client_IP, client_MAC in handler.list:
                            packet[IP].dst = client_IP
                            packet[Ether].dst = client_MAC
                            packet[Ether].src = self.OWN_MAC
                            del packet[1].chksum
                            del packet[2].chksum
                            #packet.show2()
                            threading.Thread(target=self.send_packet, args=(packet,)).start()

                    if host == "middle":
                        packet[IP].src = self.OWN_IP
                        packet[Ether].src = self.OWN_MAC
                        packet[Ether].dst = self.RMAC
                        if (packet[IP].dst not in handler.list):
                            handler.list.append(packet[IP].dst)
                        del packet[1].chksum
                        del packet[2].chksum

                        #packet.show2()
                        threading.Thread(target=self.send_packet, args=(packet,)).start()

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
        sendp(packet, iface=pktout, realtime=True)


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

    # if not verbose:
    #     print(TREDBOLD + "You are running on silent mode!")

    handler = Handler()
    lora = LoRaSocket(verbose=False)
    lora.set_bw(9)
    lora.set_freq(915)
    dns = "udp or (tcp and not (port 22))"

    Sniff = AsyncSniffer(prn=handler.pushpkt, filter="udp or icmp or (tcp and not (port 22)) or port 67 or port 68", store=False, iface=pktin)
    #Sniff = AsyncSniffer(prn=handler.pushpkt, iface="lo", filter="port 3000",store=False)
    Sniff.start()
    thread = threading.Thread(target=handler.run)
    thread.start()

    try:
        lora.set_mode(MODE.RXCONT)
        while True:
            pass
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()