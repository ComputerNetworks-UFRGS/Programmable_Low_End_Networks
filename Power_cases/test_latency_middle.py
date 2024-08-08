#!/usr/bin/env python3

import sys, threading, argparse
from time import time,sleep,monotonic
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
        self.packet_received = False
        self.timer_started = False

    def end_test(self):
        self.end = True

    def switch_mode(self):
        self.send = not self.send

    def run(self):
        while not self.end:
            if (not self.tx_wait) and self.send:
                # creates packet with xB
                payload = 'z' * 1500
                data = bytes(Ether()/IP()/TCP()/payload)
                packets = self.split(data)

                # sends the pieces one by one
                for packet in packets:
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1,0,0,0,0,0]) # set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.1) # less time for better transmision

                    if not full_packet:
                        self.switch_mode()
                        break

            sleep(0.1)
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
        self.start_time = 0
        self.end_time = 0

    # when LoRa receives data send to socket conn
    def on_rx_done(self):
        try:
            if not handler.timer_started:
                lora.start_time = monotonic()
                handler.timer_started = True
            handler.tx_wait = 1
            payload = self.read_payload(nocheck=True)
            self.payload.extend(payload)

            print(TGREEN + "Received piece!")

            if full_packet:
                if len(payload) != 127:
                    if len(self.payload) > 34:
                        print(TGREEN + "Full packet received")
                        #self.payload = []
                        #handler.tx_wait = 0
                        #handler.switch_mode()
                        #self.payload = []
                        if host == 'middle':
                            self.end_time = monotonic() #record the end time
                            total_time = self.end_time - self.start_time
                            #total_time_ms = total_time  * 1000
                            print(TREDBOLD + f"Paquet transmission time before ACK: {total_time:.4f} ms")

                            # Send ACK back to end
                            ack_packet = "ACK".encode()
                            lora.write_payload(list(ack_packet))
                            lora.set_dio_mapping([1, 0, 0, 0, 0, 0])  # Set DIO0 for txdone
                            lora.set_mode(MODE.TX)
                            print(TYELLOW + "Send ACK to raspi end")

                            self.payload = []  # Clear the payload after sending ACK
                            handler.tx_wait = 0
                            handler.switch_mode()
                            handler.packet_received = True  # Mark packet as received
                            #handler.end_test()  # Ensure the handler ends after sending the ACK
            else:
                # if was in send mode, go to receive mode and vice-versa
                handler.tx_wait = 0
                self.payload = []

            self.clear_irq_flags(RxDone=1) # clear rxdone IRQ flag
            self.reset_ptr_rx()
            if not handler.end:
                self.set_mode(MODE.RXCONT)
        except OSError as e:
            print(f"Error in on_rx_done: {e}")
            handler.end_test()

    # after data sent by LoRa reset to receive mode
    def on_tx_done(self):
        try:
            self.clear_irq_flags(TxDone=1)
            self.set_dio_mapping([0] * 6)
            self.set_mode(MODE.RXCONT)
            handler.tx_wait = 0

            if handler.packet_received:
                handler.end_test()
        except OSError as e:
            print(f"Error in on_tx_done: {e}")
            handler.end_test()


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
                #print("# Delay time: " + str(lora.delay) + "s")
                sys.exit()
            pass

    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
