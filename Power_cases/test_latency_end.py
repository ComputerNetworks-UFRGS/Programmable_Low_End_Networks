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

def get_packet_size(min_value, max_value):
    while True:
        try:
            user_input = int(input(f"Please choose the size of the packet in b (between {min_value} and {max_value}): "))
            if min_value <= user_input <= max_value:
                return user_input
            else:
                print(f"Error: The number must be between {min_value} and {max_value}. Please try again")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")

def get_repetitions():
    while True:
        try:
            user_input = int(input("Please enter the number for repetitions: "))
            if user_input > 0:
                return user_input
            else:
                print("Error: The number must be positive. Please try again.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")

class Handler:
    def __init__(self):
        self.tx_wait = 0
        self.end = False
        self.send = host == 'end'
        self.ack_received = False
        self.repetitions = get_repetitions()
        self.packet_size = get_packet_size(64, 1500)  # Packet size
        print(TYELLOW + f"Starting iteration with {self.repetitions} repetitions remaining.")
        self.thread_started = False  # Ajout d'un flag pour g

    def end_test(self):
        self.repetitions -= 1
        if self.repetitions > 0:
            self.reset_for_next_iteration()
        else:
            self.end = True
            print("All iterations completed, exiting...")
            sys.exit(0)

    def reset_for_next_iteration(self):
        sleep(1)
        print(TYELLOW + f"Starting iteration with {self.repetitions} repetitions remaining.")
        self.send = True
        self.tx_wait = 0
        self.ack_received = False

        self.reinitialize_lora_module()

        #self.run()

    def reinitialize_lora_module(self):
        print(TYELLOW + "Reinitializing LoRa module...")
        lora.set_mode(MODE.SLEEP)
        sleep(0.2)  # Ensure the LoRa module has time to enter sleep mode

        lora.set_max_payload_length(128)
        lora.set_pa_config(pa_select=1)
        lora.set_bw(9)
        lora.set_freq(915)
        lora.reset_ptr_rx()
        lora.clear_irq_flags()
        lora.set_dio_mapping([0] * 6)
        #sleep(2)
        lora.set_mode(MODE.RXCONT)
        print("LoRa module reinitialized for next iteration.")

    def run(self):
        while not self.end:
            self.thread_started = True
            if (not self.tx_wait) and self.send:
                payload = 'z' * self.packet_size
                data = bytes(Ether()/IP()/TCP()/payload)
                packets = self.split(data)

                lora.start_time = monotonic()

                # Send the pieces one by one
                for packet in packets:
                    print(f"Sending packet fragment: {packet}")
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1, 0, 0, 0, 0, 0])
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.5)  # Delay between transmissions

                # Wait until ACK is received before proceeding
                while not self.ack_received and not self.end:
                    sleep(1)
                    print("Waiting for ACK...")

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
        self.set_max_payload_length(128)
        self.set_dio_mapping([0] * 6)
        self.payload = []
        self.start_time = 0
        self.end_time = 0

    def on_rx_done(self):
        print("test")
        try:
            print("RX done, processing payload.")
            handler.tx_wait = 1
            payload = self.read_payload(nocheck=True)
            self.payload.extend(payload)

            print(f"Received payload: {payload}")

            if len(payload) == 3 and ''.join([chr(x) for x in payload]) == "ACK":
                print(TGREEN + "Received ACK!")
                self.end_time = monotonic()
                total_time = self.end_time - self.start_time
                total_time_ms = total_time * 1000
                print(f"Total Transmission time: {total_time_ms:.4f} ms")
                handler.ack_received = True
                handler.end_test()

            self.clear_irq_flags(RxDone=1)
            self.reset_ptr_rx()
            if not handler.end:
                lora.set_mode(MODE.RXCONT)

#            current_mode = self.get_mode()
#            print(f"Current LoRa mode after RX: {current_mode}")

        except OSError as e:
            print(f"Error in on_rx_done: {e}")
            handler.end_test()

    def on_tx_done(self):
        try:
#            print("TX done, clearing IRQ flags and switching to RX mode.")
            self.clear_irq_flags(TxDone=1)
            self.set_dio_mapping([0] * 6)
            lora.set_mode(MODE.RXCONT)
            handler.tx_wait = 0
            print(TYELLOW + "Send piece")

            if host == 'middle':
                handler.end_test()

        except OSError as e:
            print(f"Error in on_tx_done: {e}")
            handler.end_test()

        sleep(0.1)
        lora.set_mode(MODE.RXCONT)

if __name__ == '__main__':
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
        while True:
            sleep(0.1)  # Small delay to allow other threads to work
            if handler.end:
                break
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
