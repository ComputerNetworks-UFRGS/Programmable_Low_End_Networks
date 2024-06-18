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


import sys, asyncore, socket, threading
from time import time, sleep
from collections import Counter
from scapy.all import sniff, srp1
from scapy.layers.inet import IP, Ether
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()

# chance channels to reach a wider bandwidth
class Change_Channel(asyncore.dispatcher):
    def __init__(self, interfaceClient):
        asyncore.dispatcher.__init__(self, interfaceClient)
        self.interfaceClient = interfaceClient
        
    def change_channel():
        ch = 1
        while True:
            os.system(f"iwconfig {interface} channel {ch}")
            # switch channel from 1 to 14 each 0.5s
            ch = ch % 14 + 1
            time.sleep(0.5)

# sniffs wlan and sends packets through socket to server
class Client(threading.Thread):
    def __init__(self, host, port, interfaceClient):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.connect((host,port))

    # sniffs and handles communication with client
    def run(self):
        sniff(prn=self.send_rqst, iface=interfaceClient, count=1)
        #data = bytearray(self.sock.recv(1024)).decode('ascii')
        sniff(prn=self.recv_ans, iface=interfaceServer)
        data = str(self.sock.recv(1024)).decode('ascii')
        pkt = Ether(_pkt=data)
        dst = pkt[IP].dst
        print ('From LoRa: ' + data)
        sendp(Ether()/IP(dst=dst,ttl=(1,4)), iface="wlan0")

    #sends packet through socket to server
    def send_rqst(self, packet):
        message = bytes(packet)
        print(message)
        #print('Pacote: ')
        #print(' '.join(str(ord(char)) for char in str(packet)))
        #chunks = [message[i:i+120] for i in range(0, len(message), 120)]
        #for chunk in chunks:
        #    self.sock.send(bytearray(chunk, 'utf-8'))
        self.sock.send(message)
    
    # filters out the packets where the rasp is the destination and send
    def recv_ans(self, packet):
        dst = packet[IP].dst
        print(dst)
        if not dst == "143.50.54.38":
            message = bytes(packet)
            self.sock.send(message)
        
# responsible for the communication between the clients and lora             
class Server(asyncore.dispatcher):
    def __init__(self, host, port, interfaceServer):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)

    def handle_accepted(self, sock, addr):
        print("Connection from %s:%s" % sock.getpeername())
        self.conn = Handler(sock)
        
# handles the server's communication
class Handler(asyncore.dispatcher):
    def __init__(self, sock):
        asyncore.dispatcher.__init__(self, sock)
        self.databuffer = b""
        self.tx_wait = 0
        
    def handle_read(self):
        if not self.tx_wait:
            BOARD.led_on()
            data = self.recv(127)
            print('Send:' + str(data))
            print(len(data))
            lora.write_payload(list(data))
            lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
            lora.set_mode(MODE.TX)
            BOARD.led_off()
            self.tx_wait = 1
    
    # when data for the socket, send
    def handle_write(self):
        if self.databuffer:
            self.send(self.databuffer)
            self.databuffer = b""
            
    def handle_close(self):
        print("Client disconnected")
        self.close()
        
        
class LoRaSocket(LoRa):
    def __init__(self, verbose=False):
        super(LoRaSocket, self).__init__(verbose)
        #self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.SLEEP)
        self.set_pa_config(pa_select=1)
        self.set_max_payload_length(128) # set max payload to max fifo buffer length
        self.payload = []
        self.set_dio_mapping([0] * 6) #initialise DIO0 for rxdone  

    def on_rx_done(self):
        payload = self.read_payload(nocheck=True)
        print(len(payload))
        
        if len(payload) == 127:
            self.payload[len(self.payload):] = payload
            #self.payload.extend(payload)
        else:
            self.payload[len(self.payload):] = payload
            #self.payload.extend(payload)
            print('Recv:', str(bytes(self.payload)))
            
            server.conn.databuffer = bytes(payload)
            self.payload = []
          
        self.clear_irq_flags(RxDone=1)
        self.set_mode(MODE.SLEEP)  
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        self.set_dio_mapping([0] * 6)    
        
        self.set_mode(MODE.RXCONT)
        server.conn.tx_wait = 0

def start_asyncore_loop():
    asyncore.loop()

if __name__ == '__main__':
    interfaceClient = "wlan0"
    interfaceServer = "eth0"
    
    server = Server('127.0.0.1', 20000, interfaceServer)
    lora = LoRaSocket(verbose=False)
    client = Client('127.0.0.1', 20000, interfaceClient)
    asyncore_thread = threading.Thread(target=start_asyncore_loop)
    #channel_changer = Change_Channel(interfaceClient)

    print(lora)

    try:
        lora.set_mode(MODE.RXCONT)
        client.start()
        asyncore_thread.start()
        client.join()
        asyncore.join()
        #asyncore.loop()
    except KeyboardInterrupt:
        sys.stderr.write("\nKeyboardInterrupt\n")
    finally:
        lora.set_mode(MODE.SLEEP)
        print("Closing socket connection")
        sys.exit()
        BOARD.teardown()
