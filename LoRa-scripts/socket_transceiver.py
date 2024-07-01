#!/usr/bin/env python3
#end
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


import sys, threading
from time import time,sleep
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()

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

                # sends the pieces one by one
                for packet in packets:
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(1)

    
    def pushpkt(self, packet):
        if (packet.haslayer(IP)) and (packet.haslayer(Ether)):
            #print("A")
            #if ((packet[IP].src in self.IPlist) or (packet[IP].dst in self.IPlist)):
            #add the packets on the queue if the IP adress is known
            if packet[IP].dst in self.IPlist:
                print("pkt: "  + packet[IP].dst)
                print(self.IPlist)
                print(packet.summary())
                #the packet is converted into bytes and added to the queue
                self.pktlist.enqueue(bytes(packet))
            else:
                if packet.haslayer(BOOTP):
                    if packet[BOOTP].yiaddr not in self.IPlist:
                        print(packet.summary())
                        self.IPlist.append(packet[BOOTP].yiaddr)
                        self.pktlist.enqueue(bytes(packet))
                        print("IP: " + packet[IP].dst)
                        print(self.IPlist)
                    else:
                        self.tx_wait=0
                else:
                    self.tx_wait=0
        else:
            self.tx_wait=0

        packet = []


    def split(self, data):
        packets = []
        for i in range(0, len(data), 127):
            packet = data[i:i + 127]
            packets.append(packet)

        return packets

class LoRaSocket(LoRa):
    def __init__(self, verbose=False):
        super(LoRaSocket, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_pa_config(pa_select=1)
        self.set_max_payload_length(128) # set max payload to max fifo buffer length
        self.payload = []
        self.set_dio_mapping([0] * 6) #initialise DIO0 for rxdone

    # when LoRa receives data send to socket conn
    def on_rx_done(self):
        payload = self.read_payload(nocheck=True)

        if len(payload) == 127:
            self.payload[len(self.payload):] = payload
        else:
            self.payload[len(self.payload):] = payload

            packet = Ether(bytes(self.payload[0:len(self.payload)]))
            print("Recv: " + packet.summary())
            #print("Payload: " + str(packet))

            if packet.haslayer(BOOTP):
                if packet[BOOTP].yiaddr not in handler.IPlist:
                    handler.IPlist.append(packet[BOOTP].yiaddr)

            sendp(packet, iface="wlan0")
            self.payload = []

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
    handler = Handler()
    lora = LoRaSocket(verbose=False)
    SniffWlan = AsyncSniffer(prn=handler.pushpkt, store=False, iface="wlan0")
    SniffWlan.start()
    # SniffDHCP = AsyncSniffer(prn=handler.pushIP, store=False, iface="wlan0", filter='udp and (port 67 or port 68)')
    # SniffDHCP.start()

    print(lora)

    thread = threading.Thread(target=handler.run)
    thread.start()

    try:
        lora.set_mode(MODE.RXCONT)
        while True:
            pass

    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboardInterrupt\n")
        
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
