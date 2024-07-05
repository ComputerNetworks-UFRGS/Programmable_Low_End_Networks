#!/usr/bin/env python3
#middle
""" An asynchronous socket <-> LoRa interface """

# MIT License
#
# Copyright (c) 2016 bjcarne
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys, threading, argparse
from time import time,sleep
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()
verbose = False

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
        self.IPlist = []

    def run(self):
        while True:
            # while there are packets to send
            if (not self.tx_wait) and (not self.pktlist.isEmpty()):
                # gets a packet from the queue
                data = self.pktlist.dequeue()
                # breaks it into pieces
                packets = self.split(data)

                if (verbose):
                    print(data)

                # sends the pieces one by one
                for packet in packets:
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(1)
            sleep(1)

    def pushpkt(self, packet):
        # if is valid packet
        if (packet.haslayer(IP)) and (packet.haslayer(Ether)):
            if verbose:
                print(packet.summary())
            
            # if it's a known IP
            if host == "end":
                Filter = packet[IP].src
            else:
                Filter = packet[IP].dst

            if Filter in self.IPlist:
                # the packet is converted into bytes and added to the queue
                self.pktlist.enqueue(bytes(packet))
                #print(packet.summary())
            else:
                if packet.haslayer(BOOTP):
                    if (packet[BOOTP].yiaddr not in self.IPlist) and (pktin == "wlan0"):
                        self.IPlist.append(packet[BOOTP].yiaddr)
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

    # when LoRa receives data send to socket conn
    def on_rx_done(self):
        handler.tx_wait = 1
        payload = self.read_payload(nocheck=True)
        self.payload += payload
        # if piece received is the last one
        if len(payload) != 127:
            packet = Ether(bytes(self.payload))

            if (verbose):
                print("Packet in!  " + packet.summary())

            # if it's a DHCP packet
            if packet.haslayer(BOOTP):
                if packet[BOOTP].yiaddr not in handler.IPlist:
                    handler.IPlist.append(packet[BOOTP].yiaddr)

            # sends packet to network
            sendp(packet, iface=pktout, realtime=True)
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


if __name__ == '__main__':
    #./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -v
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", dest="pktin", default="lorarecv", help="Sniffed Interface (packet in)", required=False)
    parser.add_argument("-o", "--out", dest="pktout", default="lorasend", help="Send Interface (packet out)", required=False)
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose mode", action='store_true')
    parser.add_argument("-m", "--mode", dest="mode", default="end", help="which host is running the code", required=False)
    args = parser.parse_args()
    pktin = args.pktin
    pktout = args.pktout
    host = args.mode
    verbose = args.verbose

    if not verbose:
        print("You are running on silent mode!")

    handler = Handler()
    lora = LoRaSocket(verbose=False)
    lora.set_bw(9)
    lora.set_freq(915)
    # filter only DHCP packets: port 68 and port 67
    #dhcp_pkts = 'port 68 and port 67'
    # remove ssh packets: not port 22
    SniffWlan = AsyncSniffer(prn=handler.pushpkt, store=False, iface=pktin)
    SniffWlan.start()
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
