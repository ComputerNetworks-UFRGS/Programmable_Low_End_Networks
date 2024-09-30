#!/usr/bin/env python3

import sys, threading, argparse
from time import time,sleep
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD
from socket import *
from timeit import default_timer as timer

BOARD.setup()
verbose = False

TREDBOLD =  '\033[31;1m'
TGREEN =  '\033[32m' 
TYELLOW =  '\033[33m'

class Handler:
    def __init__(self):
        self.tx_wait = 0
        self.end = False
        self.send = host == 'end'

    def end_test(self):
        self.end = True

    def switch_mode(self):
        self.send = not self.send

    def run(self):
        while not self.end:
            if (not self.tx_wait) and self.send:
                if host == 'end':
                    lora.delay = time.process_time()

                # creates packet with 1500B
                payload = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
                data = bytes(Ether()/IP()/TCP()/payload)
                packets = self.split(data)

                # sends the pieces one by one
                for packet in packets:
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.5) # less time for better transmision

                    if not full_packet:
                        self.switch_mode()
                        break

            sleep(0.5)
        print("exit")
        sys.exit()

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
        self.set_dio_mapping([0] * 6) #initialise DIO0 for rxdone
        self.payload = []
        self.delay = 0

    # when LoRa receives data send to socket conn
    def on_rx_done(self):
        handler.tx_wait = 1
        payload = self.read_payload(nocheck=True)
        self.payload += payload

        print(TGREEN + "Received piece!")

        if full_packet:
            if len(payload) != 127:
                if len(self.payload) > 34:
                    print(TGREEN + "Full packet received")
                    self.payload = []
                    handler.tx_wait = 0
                    handler.switch_mode()
                    self.payload = ""
        else:
            # if was in send mode, go to receive mode and vice-versa
            handler.tx_wait = 0
            self.payload = []

        if host == 'end':
            print("End of RTL test")
            self.delay = time.process_time() - self.delay
            handler.end_test();

        self.clear_irq_flags(RxDone=1) # clear rxdone IRQ flag
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    # after data sent by LoRa reset to receive mode
    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1) # clear txdone IRQ flag
        self.set_dio_mapping([0] * 6)
        self.set_mode(MODE.RXCONT)
        handler.tx_wait = 0

        if host == 'middle':
            handler.end_test()

        print(TYELLOW + "Sent piece")


if __name__ == '__main__':
    #./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -v
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", dest="mode", default="end", help="which host is running the code", required=False)
    parser.add_argument("-f", "--full-packet", dest="full_packet", help="Send full packet or only 127B", action='store_true')
    args = parser.parse_args()
    host = args.mode
    full_packet = args.full_packet
    send = (host == 'end')

    handler = Handler()
    lora = LoRaSocket(verbose=True)
    lora.set_bw(9)
    lora.set_freq(915)

    thread = threading.Thread(target=handler.run)
    thread.start()

    try:
        lora.set_mode(MODE.RXCONT)
        while True:
            if handler.end:
                print("# Delay time: " + str(lora.delay) + "s")
                sys.exit()
            pass

    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()