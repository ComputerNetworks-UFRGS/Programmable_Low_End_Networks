#!/usr/bin/env python3

from SX127x_module import SX127x_PLEN
import sys, threading, argparse, socket
from time import sleep, time
from collections import deque

TREDBOLD = '\033[31;1m'
TGREEN = '\033[32m'
TYELLOW = '\033[33m'
PKTIN = "lorasend"
PKTOUT = "lorarecv"
BW = 9
SF = 7
FREQ = 868

'''
Handler - handles sending and receiving of packets

Attributes:
	lock (threading.Lock): lock to ensure thread safety
	transceiver: Transceiver API
	controller (Controller): controller class instance.
'''
class Handler(threading.Thread):
	def __init__(self, lock, transceiver, controller):
		super().__init__()
		self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
		self.sock.bind((PKTIN, 0))
		self.sock.setblocking(False)	
		self.daemon = True
		self.packets = deque()
		self.controller = controller
		self.transceiver = transceiver
		self.lock = lock
		self.count = 0
		
	def run(self):
		while True:
			# while receiving packet
			while self.controller.getRxWait():
				with self.lock:
					self.controller.setRxWait(False)
				#sleep(1)

			# send packets
			if not self.controller.wait_res and not self.controller.wait() and len(self.packets):
				packet = self.packets.popleft()
				transceiver.send(packet)
				self.count = time()
				print('queue size: ' + str(len(self.packets)))
				self.controller.wait_res = True

			if time() - self.count >=1:
				self.controller.wait_res = False

			# recv packets
			try:
				data = self.sock.recvfrom(255)
				self.packets.append(bytes(data[0]))
			except BlockingIOError:
				pass

	def shutdown(self):
		self.sock.close()

'''
Controller class

Handles flags to avoid colisions while receiving
and transmitting packets.

Attributes:
	tx_wait (Bool): avoids writting to antenna while it's in use.
	rx_wait (Bool): avoids switching to transmittion mode while
		receiving sliced packets.
'''
class Controller():
	def __init__(self):
		self.tx_wait = False
		self.rx_wait = False
		self.wait_res = False

	def setTxWait(self, val):
		self.tx_wait = val

	def getTxWait(self):
		return self.tx_wait

	def setRxWait(self, val):
		self.rx_wait = val
	
	def getRxWait(self):
		return self.rx_wait
	
	def wait(self):
		return self.tx_wait and self.rx_wait
	

if __name__ == '__main__':
	lock = threading.Lock()
	controller = Controller()
	transceiver = SX127x_PLEN(lock, PKTOUT, controller, BW, SF, FREQ)
	handler = Handler(lock, transceiver, controller)

	handler.start()

	try:
		transceiver.start()
		while True:
			sleep(1)

	finally:
		transceiver.shutdown()
		handler.shutdown()
