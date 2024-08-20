#!/usr/bin/env python3

import sys, threading, argparse
import psutil, time, os
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

def timestamp():
    """Returns the time elapsed since the program started."""
    return f"[{monotonic() - lora.start_time:.4f}s] "

def get_packet_size(min_value, max_value):
    """Prompts the user to input the packet size within a specified range."""
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
    """Prompts the user to input the number of repetitions."""
    while True:
        try:
            user_input = int(input("Please enter the number for repetitions: "))
            if user_input > 0:
                return user_input
            else:
                print("Error: The number must be positive. Please try again.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")

def get_ttl(packet):
    """Returns the TTL value from the IP layer of the packet, if it exists."""
    if packet.haslayer(IP):
        return packet[IP].ttl
    else:
        return None

class Handler:
    """Handles the main logic of sending packets, managing iterations, and tracking transmission times."""
    def __init__(self):
        self.tx_wait = 0
        self.end = False
        self.send = host == 'end'
        self.ack_received = False
        self.repetitions = get_repetitions()
        self.packet_size = get_packet_size(64, 1500)
        self.iteration_start_time = None
        print(TYELLOW + f"Starting iteration with {self.repetitions} repetitions remaining.")
        self.thread_started = False
        self.timer_started = False
        self.iteration_times = []

    def end_test(self):
        """Ends the current test iteration and resets for the next one if needed, or finishes all iterations."""
        self.repetitions -= 1
        if self.repetitions > 0:
            self.reset_for_next_iteration()
        else:
            self.calculate_average_time()
            self.end = True
            print(timestamp() + f"All iterations completed, exiting...")
            sys.exit(0)

    def calculate_average_time(self):
        """Calculates and prints the average transmission time for all iterations."""
        if self.iteration_times:
            average_time = sum(self.iteration_times) / len(self.iteration_times)
            print(TGREEN + timestamp() + f"Average transmission time: {average_time:.4f}s")
        else:
            print(TREDBOLD + timestamp() + "No iteration times recorded.")

    def reset_for_next_iteration(self):
        """Resets the state for the next test iteration."""
        sleep(1)
        print(TYELLOW + timestamp() +  f"{self.repetitions} repetitions remaining.")
        self.send = True
        self.tx_wait = 0
        self.ack_received = False

        self.reinitialize_lora_module()

        self.iteration_start_time = monotonic()

    def reinitialize_lora_module(self):
        """Reinitializes the LoRa module for the next iteration."""
        lora.set_mode(MODE.SLEEP)
        lora.set_max_payload_length(128)
        lora.set_pa_config(pa_select=1)
        lora.set_bw(9)
        lora.set_freq(915)
        lora.reset_ptr_rx()
        lora.clear_irq_flags()
        lora.set_dio_mapping([0] * 6)
        lora.set_mode(MODE.RXCONT)

    def run(self):
        """Main loop for sending packets, waiting for ACKs, and managing the test flow."""
        self.iteration_start_time = monotonic()

        while not self.end:
            if (not self.tx_wait) and self.send:
                if not handler.timer_started:
                    lora.start_time = monotonic()
                    handler.timer_started = True

                payload = 'z' * self.packet_size
                data = Ether()/IP()/TCP()/payload

                ttl = get_ttl(data)
                if ttl is not None:
                    print(f"TTL of the packet: {ttl}")

                packets = self.split(bytes(data))

                # Send the pieces one by one
                for packet in packets:
                    print(timestamp() + f"Sending packet fragment: {packet}")
                    lora.write_payload(list(packet))
                    lora.set_dio_mapping([1, 0, 0, 0, 0, 0])
                    lora.set_mode(MODE.TX)
                    self.tx_wait = 1
                    sleep(0.5)

                # Wait until ACK is received before proceeding
                while not self.ack_received and not self.end:
                    sleep(1)
                    print(timestamp() + "Waiting for ACK...")

            sleep(0.5)
        print(timestamp() + f"exit")
        sys.exit()

    def split(self, data):
        """Splits data into chunks that fit into the LoRa payload."""
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
        """Handles the event when a packet is received."""
        try:
            handler.tx_wait = 1
            payload = self.read_payload(nocheck=True)
            self.payload.extend(payload)

            if len(payload) == 3 and ''.join([chr(x) for x in payload]) == "ACK":
                print(TGREEN + timestamp() + "Received ACK!")
                self.end_time = monotonic()

                # Calculate iteration time
                iteration_time = self.end_time - handler.iteration_start_time
                print(timestamp() + f"Iteration Transmission time: {iteration_time:.4f}s")

                handler.iteration_times.append(iteration_time)
                handler.ack_received = True
                handler.end_test()

            self.clear_irq_flags(RxDone=1)
            self.reset_ptr_rx()
            if not handler.end:
                lora.set_mode(MODE.RXCONT)

        except OSError as e:
            print(f"Error in on_rx_done: {e}")
            handler.end_test()

    def on_tx_done(self):
        """Handles the event when a packet has been successfully transmitted."""
        try:
            self.clear_irq_flags(TxDone=1)
            self.set_dio_mapping([0] * 6)
            sleep(0.1)
            self.set_mode(MODE.RXCONT)
            handler.tx_wait = 0
            print(TYELLOW + timestamp() + "Send piece")

            if host == 'middle':
                handler.end_test()

        except OSError as e:
            print(f"Error in on_tx_done: {e}")
            handler.end_test()

        sleep(0.1)
        lora.set_mode(MODE.RXCONT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", dest="pktin", default="wlan0", help="Sniffed Interface (packet in)", required=False)
    parser.add_argument("-o", "--out", dest="pktout", default="lorarecv", help="Send Interface (packet out)", required=False)
    parser.add_argument("-m", "--mode", dest="mode", default="end", help="which host is running the code", required=False)
    parser.add_argument("-f", "--full-packet", dest="full_packet", help="Send full packet or only 127B", action='store_true')
    args = parser.parse_args()
    pktin = args.pktin
    pktout = args.pktout
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
