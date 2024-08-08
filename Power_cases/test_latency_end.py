#!/usr/bin/env python3

import sys, threading, argparse
from time import sleep, monotonic
from scapy.all import *
from SX127x.LoRa import *
from SX127x.board_config import BOARD
from socket import *

BOARD.setup()
verbose = False

TREDBOLD = '\033[31;1m'
TGREEN = '\033[32m'
TYELLOW = '\033[33m'

class Handler:
    def __init__(self):
        self.tx_wait = 0
        self.end = False
        self.send = host == 'end'
        self.ack_received = False  # Add flag to indicate if ACK was received
        self.round_trip_times = []  # List to store round-trip times
        self.tx_time = 0
        self.rx_time = 0
        self.pi_time = 0  # Raspberry Pi operational time
        self.timer_started = False

    def end_test(self):
        self.end = True
        self.calculate_energy()  # Calculate energy consumption

    def switch_mode(self):
        self.send = not self.send

    def run(self):
        while not self.end:
            if (not self.tx_wait) and self.send:

                # Create packet with xB
                payload = 'z' * 100
                data = bytes(Ether()/IP()/TCP()/payload)
                packets = self.split(data)
                lora.start_time = monotonic()  # Start timing

                # Send the pieces one by one
                for packet in packets:
                    print(f"Sending packet fragment: {packet}")  # Log packet being sent
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1, 0, 0, 0, 0, 0])  # Set DIO0 for txdone
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.5)  # Time between transmissions

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

    def calculate_energy(self):
        P_TX = 120 / 1000  # watts
        P_RX = 10 / 1000   # watts
        P_PI = 5  # Power consumption of Raspberry Pi 4 in watts
        E_TX = P_TX * self.tx_time  # Energy for TX
        E_RX = P_RX * self.rx_time  # Energy for RX
        E_PI = P_PI * self.pi_time  # Energy for Raspberry Pi operation
        total_energy = E_TX + E_RX + E_PI  # Total energy in joules
        print(f" ")
        print(f"Energy consumed for TX: {E_TX:.6f} joules")
        print(f"Energy consumed for RX: {E_RX:.6f} joules")
        print(f"Energy consumed for Raspberry Pi: {E_PI:.6f} joules")
        print(f"Total energy consumed: {total_energy:.6f} joules")

class LoRaSocket(LoRa):
    def __init__(self, verbose=verbose):
        super(LoRaSocket, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_pa_config(pa_select=1)
        self.set_max_payload_length(128)  # Set max payload to max FIFO buffer length
        self.set_dio_mapping([0] * 6)  # Initialize DIO0 for rxdone
        self.payload = []
        self.start_time = 0
        self.end_time = 0

    # When LoRa receives data, send to socket conn
    def on_rx_done(self):
        try:
            #if not handler.timer_started:  # Ajouté
            #    handler.rx_start_time = monotonic()  # Ajouté
            #    handler.timer_started = True  # Ajout

            handler.timer_started = True
            handler.rx_start_time = monotonic()  # Start RX time
            handler.tx_wait = 1
            payload = self.read_payload(nocheck=True)
            self.payload.extend(payload)  # Correctly handle received payload as a list

            if len(payload) == 3 and ''.join([chr(x) for x in payload]) == "ACK":
                # Received ACK
                print(TGREEN + "Received piece!")
                self.end_time = monotonic()
                total_time = self.end_time - self.start_time
                total_time_ms = total_time * 1000
                print(f"Total Transmission time: {total_time_ms:.4f} ms")
                handler.round_trip_times.append(total_time)  # Store round-trip time
                handler.ack_received = True  # Set ACK received to True
                handler.end_test()

            if full_packet:
                if len(payload) != 127:
                    if len(self.payload) > 34:
                        print(TGREEN + "Full packet received")
                        self.payload = []
                        handler.tx_wait = 0
                        handler.switch_mode()
                        self.payload = []
            else:
                handler.tx_wait = 0
                self.payload = []

            #handler.rx_time += monotonic() - handler.rx_start_time  # Ajouté
            #print(f"Updated RX time: {handler.rx_time:.6f} seconds")  # Ajouté

            self.clear_irq_flags(RxDone=1)  # Clear rxdone IRQ flag
            self.reset_ptr_rx()
            if not handler.end:
                self.set_mode(MODE.RXCONT)
        except OSError as e:
            print(f"Error in on_rx_done: {e}")
            handler.end_test()

    # After data sent by LoRa, reset to receive mode
    def on_tx_done(self):
        #handler.tx_time += monotonic() - lora.start_time  # Ajout
        #print(f"Updated TX time: {handler.tx_time:.6f} seconds")  # Ajout

        self.clear_irq_flags(TxDone=1)  # Clear txdone IRQ flag
        self.set_dio_mapping([0] * 6)
        self.set_mode(MODE.RXCONT)
        handler.tx_wait = 0

        if host == 'middle':
            handler.end_test()

        print(TYELLOW + "Sent piece")

if __name__ == '__main__':
    # ./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -v
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