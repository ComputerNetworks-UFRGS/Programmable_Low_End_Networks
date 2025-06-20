import RPi.GPIO as GPIO
import serial
import time
import threading
import socket

class SX126x_PLEN:
    M0 = 22
    M1 = 27
    AUX = 17  
    

    UART_BAUDRATE_9600 = 0x60
    PACKAGE_SIZE = {
        240: 0x00,
        128: 0x40,
        64: 0x80,
        32: 0xC0
    }

    AIR_SPEED = {
        1200: 0x01,
        2400: 0x02,
        4800: 0x03,
        9600: 0x04,
        19200: 0x05,
        38400: 0x06,
        62500: 0x07
    }

    POWER = {
        22: 0x00,
        17: 0x01,
        13: 0x02,
        10: 0x03
    }

    def __init__(self, serial_port, pktout, controller, lock,
                 freq=868, addr=0xFFFF, power=22,
                 air_speed=2400, net_id=0, buffer_size=240,
                 crypt=0, m0_pin=M0, m1_pin=M1, aux_pin=AUX):
        
        self.serial_port = serial_port
        self.controller = controller
        self.lock = lock
        self.pktout = pktout
        self.m0 = m0_pin
        self.m1 = m1_pin
        self.aux = aux_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.m0, GPIO.OUT)
        GPIO.setup(self.m1, GPIO.OUT)
        GPIO.setup(self.aux, GPIO.IN)

        self.ser = serial.Serial(serial_port, 9600, timeout=0.5)
        self.ser.flushInput()

        self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x800))
        self.sock.bind((pktout, socket.htons(0x800)))

        self.cfg_reg = [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00,
                        0x62, 0x00, 0x12, 0x43, 0x00, 0x00]
        
        self._configure(freq, addr, power, air_speed, net_id, buffer_size, crypt)

    def _wait_aux_high(self, timeout=2.0):
        start = time.time()
        while GPIO.input(self.aux) == 0:
            if time.time() - start > timeout:
                raise TimeoutError("Erro no AUX pin")
            time.sleep(0.01)

    def _configure(self, freq, addr, power, air_speed, net_id, buffer_size, crypt):
        GPIO.output(self.m0, GPIO.LOW)
        GPIO.output(self.m1, GPIO.HIGH)
        time.sleep(0.1)

        high_addr, low_addr = (addr >> 8) & 0xFF, addr & 0xFF
        freq_offset = freq - 850 if freq >= 850 else freq - 410

        air_speed_val = self.AIR_SPEED.get(air_speed, 0x02)
        buffer_size_val = self.PACKAGE_SIZE.get(buffer_size, 0x00)
        power_val = self.POWER.get(power, 0x00)

        self.cfg_reg[3:6] = [high_addr, low_addr, net_id]
        self.cfg_reg[6] = self.UART_BAUDRATE_9600 + air_speed_val
        self.cfg_reg[7] = buffer_size_val + power_val + 0x20
        self.cfg_reg[8] = freq_offset
        self.cfg_reg[9] = 0x43
        self.cfg_reg[10] = (crypt >> 8) & 0xFF
        self.cfg_reg[11] = crypt & 0xFF

        for _ in range(2):
            self.ser.write(bytes(self.cfg_reg))
            time.sleep(0.2)
            if self.ser.in_waiting > 0 and self.ser.read(1) == b'\xC1':
                break
            self.ser.flushInput()
        else:
            raise RuntimeError("SX126x configuration failed")

        GPIO.output(self.m0, GPIO.LOW)
        GPIO.output(self.m1, GPIO.LOW)
        self._wait_aux_high()

    def start(self):    
        self._wait_aux_high()
        print("RX mode")
        time.sleep(1.0)
        self.ser.reset_input_buffer() 
        
        #roda so uma vez
        if not hasattr(self, '_rx_thread') or not self._rx_thread.is_alive():
            self._rx_thread = threading.Thread(target=self.receive, daemon=True)
            self._rx_thread.start()


    def receive(self):
        while True:
            if self.controller.getTxWait(): # teoricamente nao precisa
                time.sleep(0.01)  
                continue
        
            if self.ser.in_waiting > 0:
                payload = self.ser.read(self.ser.in_waiting)
                payload = payload[6:]
                self.on_rx_done(payload)
                
    def build_antena_header(self, dest_addr=0xFFFF):
        dest_high = (dest_addr >> 8) & 0xFF
        dest_low = dest_addr & 0xFF
        src_high = self.cfg_reg[3]
        src_low = self.cfg_reg[4]
        freq_offset = self.cfg_reg[8]
        return bytes([dest_high, dest_low, freq_offset, src_high, src_low, freq_offset])

    def send(self, data: bytes):
        self._wait_aux_high()

        self.controller.setTxWait(True)
        data_with_header = self.buil_antena_header() + data
        self.ser.write(data_with_header)
        print(f"{len(data)} bytes sent")

        self._wait_aux_high()
        self.on_tx_done()

    def on_rx_done(self, payload):
        if self.fragmented_packet(payload):
            with self.lock:
                self.controller.setRxWait(True)
        print(payload)
        self.sock.send(payload)
        self.controller.wait_res = False
        print(f"{len(payload)} bytes recv")

    def on_tx_done(self):
        self.controller.setTxWait(False)
        self.start()

    def fragmented_packet(self, payload):
        offset = 5
        return (payload[20] & (1 << offset)) != 0 

    def shutdown(self):
        GPIO.output(self.m0, GPIO.HIGH)
        GPIO.output(self.m1, GPIO.HIGH)
        time.sleep(0.1)
        self.ser.close()
        self.sock.close()
        GPIO.cleanup()
