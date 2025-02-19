#!/usr/bin/env python3

from SX127x.LoRa import *
from SX127x.board_config import BOARD
import socket

'''
sx127X LoRa antenna module for Programmable Low-End Networks

Arguments:
	lock (threading.Lock): lock to ensure thread safety
	pktout (string): Interface for socket connection to forward received packets
	controller (Controller): Controller class instance.
	bw (Int): Band Width (6-9)
	sf (Int): Spreading Factor (6-12)
	freq (Int): Frequency
'''

TGREEN = '\033[32m'
TYELLOW = '\033[33m'

class SX127x_PLEN(LoRa):
	def __init__(self, lock, pktout, controller, bw, sf, freq):
		BOARD.setup()
		super().__init__(False) # verbose
		self.set_mode(MODE.SLEEP)
		self.set_pa_config(pa_select=1)
		self.set_max_payload_length(255)
		self.set_dio_mapping([0] * 6)
		self.controller = controller
		self.set_bw(bw)
		self.set_spreading_factor(sf)
		self.set_freq(freq)
		self.lock = lock
	
		# Socket with PKTOUT (reiceved from antenna) 
		self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x800))
		self.sock.bind((pktout, socket.htons(0x800)))
	
	# writes to antenna 
	def send(self, packet):
		self.write_payload(list(packet))
		self.set_dio_mapping([1,0,0,0,0,0])
		self.set_mode(MODE.TX)
		self.controller.setTxWait(True)
		print(TYELLOW + "Sent " + f'{len(packet)}' + " bytes")


	# clear rcv flags nd prepare antenna for new tx/rx
	def on_rx_done(self):
		self.clear_irq_flags(RxDone=1)
		self.reset_ptr_rx()
		payload = self.read_payload(nocheck=True)	

		if self.fragmented_packet(payload):
			with self.lock:
				self.controller.setRxWait(True)

		self.sock.send(bytes(payload))
		print(TGREEN + "DEBUG" + f'{len(payload)}' + " bytes in!")

	# Reset LoRa after transmission
	def on_tx_done(self):
		self.clear_irq_flags(TxDone=1)
		self.set_dio_mapping([0] * 6)
		self.set_mode(MODE.RXCONT)
		
		self.controller.setTxWait(False)
	
	# Test the More Fragments (MF) Bit with bitwise
	# mask to see if packet is sliced
	def fragmented_packet(self, payload):
		offset = 5
		return (payload[20] & (1 << offset)) != 0

	# Signal the PayloadProcessor to exit and clean up
	def shutdown(self):
		self.set_mode(MODE.SLEEP)
		self.sock.close()
		BOARD.teardown()

	def start(self):
		self.set_mode(MODE.SLEEP)
		print(self)

