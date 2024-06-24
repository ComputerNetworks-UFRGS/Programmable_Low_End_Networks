#!/usr/bin/env python3

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
from time import time
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
        #self.databuffer = b""
        self.tx_wait = 0
        self.pktlist = Queue()
        self.IPlist = []

    def run(self):
        while True:
            if (not self.tx_wait) and (not self.pktlist.isEmpty()):
                data = self.pktlist.dequeue()
                #print("Send: " + str(data))
                #print(len(data))
                lora.write_payload(list(data))
                lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                lora.set_mode(MODE.TX)
                self.tx_wait = 1 

        

    def pushpkt(self,packet):
        if (IP in packet) and (Ether in packet):
            #if not (packet[IP].dst == '169.254.61.68'):
            if (packet[IP].src in self.IPlist):
                print("B")
                #print("Send: " + packet)
                #print(packet[IP].dst)
                #print(packet[IP].src)
                print(packet.summary())
                self.pktlist.enqueue(bytes(packet))
                #print(self.q.size())
        #self.q.enqueue("A")

    def pushIP(self,packet):
        if (packet.haslayer(Ether) and (packet.getlayer(BOOTP).yiaddr not in self.IPlist)):
            print("A")
            self.IPlist.append(packet.getlayer(BOOTP).yiaddr)
            print(self.IPlist)
            self.pktlist.enqueue(bytes(packet))

    # when data is available on socket send to LoRa
    #def handle_read(self):
    #    if (not self.tx_wait) and (not self.q.isEmpty()):
     #       data = self.q.dequeue
      #      print("Send: " + data)
       #     lora.write_payload(list(data))
        #    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
         #   lora.set_mode(MODE.TX)
          #  self.tx_wait = 1 
    
    # when data for the socket, send
   # def handle_write(self):
        #sniff
        
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
        print("LoRa")
        payload = self.read_payload(nocheck=True)
        
        if len(payload) == 127:
            self.payload[len(self.payload):] = payload
        else:
            self.payload[len(self.payload):] = payload
            #print('Recv:' + self.payload)
            
            packet = Ether(self.payload)
            print("Recv: " + packet.summary())
            #sendp(packet, iface="eth0")
            sendp(packet, iface="wlan0")
            #server.conn.databuffer = bytes(self.payload) #send to socket conn
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
    SniffDHCP = AsyncSniffer(prn=handler.pushIP, store=False, iface="wlan0", filter='udp and (port 67 or port 68)')
    SniffDHCP.start()

    print(lora)
    
    thread = threading.Thread(target=handler.run)
    thread.start()

    thread.join()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboardInterrupt\n")
        
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
