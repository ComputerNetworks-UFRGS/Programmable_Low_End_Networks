#!/usr/bin/env python3

import sys, threading, argparse
from time import time, sleep, monotonic
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

def timestamp():
    """Returns the time elapsed since the program started."""
    return f"[{monotonic() - lora.start_time:.4f}s] "

class Handler:
    def __init__(self):
        self.tx_wait = 0
        self.end = False
        self.send = host == 'end'
        self.packet_received = False
        self.timer_started = False
        self.packet_counter = 0  # Initialize a packet counter
        self.iteration_start_time = None

    def end_test(self):
        """Ends the current test and sets the end flag."""
        self.end = True

    def switch_mode(self):
        """Switches between send and receive modes."""
        self.send = not self.send

    def run(self):
        """Main loop for sending packets, waiting for ACKs, and managing the test flow."""
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
        print(timestamp() + "exit")
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
        self.set_max_payload_length(128) # set max payload to max fifo buffer length
        self.set_dio_mapping([0] * 6) #initialise DIO0 for rxdone
        self.payload = []
        self.start_time = 0
        self.end_time = 0

    def on_rx_done(self):
        """Handles the event when a packet is received."""
        try:
            if not handler.timer_started:
                lora.start_time = monotonic()
                handler.timer_started = True

            handler.iteration_start_time = monotonic()
            handler.tx_wait = 1
            payload = self.read_payload(nocheck=True)
            self.payload.extend(payload)
            print(TGREEN + "Received piece!")

            if full_packet:
                if len(payload) != 127:
                    if len(self.payload) > 34:
                        handler.packet_counter += 1
                        print(TGREEN + timestamp() + f"Full packet {handler.packet_counter} received")
                        if host == 'middle':
                            self.end_time = monotonic() #record the end time
                            packet_time = self.end_time - handler.iteration_start_time
                            total_time = self.end_time - handler.iteration_start_time
                            print(TREDBOLD + timestamp() + f"Paquet transmission time before ACK {handler.packet_counter}: {total_time:.4f}s")

                            # Send ACK back to end
                            sleep(1)
                            ack_packet = "ACK".encode()
                            lora.write_payload(list(ack_packet))
                            lora.set_dio_mapping([1, 0, 0, 0, 0, 0])  # Set DIO0 for txdone
                            lora.set_mode(MODE.TX)
                            print(TYELLOW + timestamp() + f"Send ACK {handler.packet_counter} to raspi end")

                            self.payload = []  # Clear the payload after sending ACK
                            handler.tx_wait = 0
                            handler.packet_received = True  # Mark packet as received

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
        """Handles the event when a packet has been successfully transmitted."""
        try:
            self.clear_irq_flags(TxDone=1)
            self.set_dio_mapping([0] * 6)
            self.set_mode(MODE.RXCONT)
            handler.tx_wait = 0
            handler.packet_received = False  # Reset for the next packet

        except OSError as e:
            print(f"Error in on_tx_done: {e}")
            handler.end_test()

if __name__ == '__main__':
    #./transceiver.py -i INTERFACE_IN -o INTERFACE_OUT -m mode -f full_packet
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", dest="pktin", default="int0", help="Sniffed Interface (packet in)", required=False)
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
        lora.set_mode(MODE.RXCONT)
        while True:
            if handler.end:
                sys.exit()
            pass

    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
