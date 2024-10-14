#!/usr/bin/env python3

import sys, threading, argparse
from time import sleep, time, monotonic
from collections import deque
#from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import socket
import struct
import multiprocessing
import queue

BOARD.setup()
verbose = False

TREDBOLD = '\033[31;1m'
TGREEN = '\033[32m'
TYELLOW = '\033[33m'

lock = threading.Lock()

class Handler(threading.Thread):
    def __init__(self):
        super().__init__()
        self.tx_wait = False
        self.rx_wait = False
        self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        self.sock.bind((pktin, 0))
        self.daemon = True
        self.sock.setblocking(False)
        self.packets = deque()
        self.time = 0
        self.start_time = [0] * 100
        self.seq_num = 0

    def run(self):
        seq_num = 0
        while True:
            while self.rx_wait:
                with lock:
                    self.rx_wait = 0
                #sleep(0.6)
            if not (self.tx_wait or self.rx_wait) and len(self.packets): # If not waiting for transmission and packets in queue
                packet = self.packets.popleft()
                lora.write_payload(list(packet)) # Writes packet for transmission
                lora.set_dio_mapping([1,0,0,0,0,0]) # Set lora for TXdone
                print(TYELLOW + "Sent " + f'{len(packet)}' + " bytes")
                lora.set_mode(MODE.TX)
                self.tx_wait = True
            try: # Non-blocking Recv function, receives up to 1500 bytes
                data = self.sock.recvfrom(255)
                self.time = time()

                #self.time = time()
                if mode:
                    if mode == "simple-forward":
                        self.seq_num = data[0][41]
                        print(self.seq_num)

                else:
                    self.seq_num += 1

                self.start_time[self.seq_num] = self.time
                self.packets.append(bytes(data[0]))

            except BlockingIOError:
                pass

class LoRaSocket(LoRa):
    def __init__(self, verbose=verbose):
        super(LoRaSocket, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_pa_config(pa_select=1)
        self.set_max_payload_length(255)  # set max payload to max fifo buffer length
        self.set_dio_mapping([0] * 6)  # initialise DIO0 for rxdone
        self.time = 0
        self.finish_time = [0] * 100

        self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        self.sock.bind((pktout, socket.htons(0x0800)))
        self.seq_num = 0

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)  # clear receive flags and prepare antenna for new tx/rx
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

        payload = self.read_payload(nocheck=True)  # Reads the antenna

        if mode:
            if mode == "simple-forward":
                if self.testBit(payload[20], 5):
                    with lock:
                        handler.rx_wait = 1
            else:
                if self.testBit(payload[6], 5):
                    with lock:
                        handler.rx_wait = 1


        print(TGREEN + "DEBUG " + f'{len(payload)}' + " bytes in!")
        self.send_packet(bytes(payload))
        self.time = time()
        if mode:
            if mode == "simple-forward":
                self.seq_num = payload[41]
                print(f'finish_time: {self.seq_num}')
        else:
            self.seq_num += 1
        self.finish_time[self.seq_num] = self.time
        #Put the new payload into the queue for processing

    def on_tx_done(self):  # Resets LoRa after transmission
        self.clear_irq_flags(TxDone=1)
        self.set_dio_mapping([0] * 6)
        self.set_mode(MODE.RXCONT)
        handler.tx_wait = 0

    def testBit(self, int_val, offset):  # Tests if the bit in the offset is zero
        return (int_val & (1 << offset)) != 0

    def send_packet(self, packet):
        self.sock.send(packet)

if __name__ == '__main__':
    #./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -v
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose mode", action='store_true')
    parser.add_argument("-m", "--mode", dest="mode", default='',help="Compression mode", type=str, required=False)
    args = parser.parse_args()
    verbose = args.verbose
    mode = args.mode
    pktin = "lorasend"
    pktout = "lorarecv"

    handler = Handler()
    lora = LoRaSocket(verbose=verbose)
    lora.set_bw(9)
    lora.set_spreading_factor(7)
    lora.set_freq(915)
    print(lora)

    handler.start()

    try:
        lora.set_mode(MODE.RXCONT)
        while True:
            sleep(1)
    except KeyboardInterrupt:
        for j in range(1, 100):
            if lora.finish_time[j]:
                print(f'{j}: {lora.finish_time[j] - handler.start_time[j]}')
    finally:
        lora.set_mode(MODE.SLEEP)
        lora.sock.close()
        handler.sock.close()
        BOARD.teardown()