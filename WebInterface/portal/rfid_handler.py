import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal
import time
import sys
import os
import traceback
import threading
from django.db import connection

##################################
# Pin connections for RFID-RC522 #
##########################################################################################
#[MFRC522 Pin]  [Raspberry Pi Pin]  [BCM GPIO Number]   [Pin Function]                   #
# SDA (SS)	     Pin 24	             GPIO8               SPI0 CE0 (Chip Enable)          #
# SCK	         Pin 23	             GPIO11              SPI0 SCLK (Clock)               #
# MOSI	         Pin 19	             GPIO10              SPI0 MOSI (Master Out Slave In) #
# MISO	         Pin 21	             GPIO9               SPI0 MISO (Master In Slave Out) #
# IRQ	         Not connected	     -	                 Interrupt (Optional)            #
# GND	         Pin 6	             Ground	             Ground                          #
# RST	         Pin 22	             GPIO25	             Reset                           #
# 3.3V	         Pin 1	             3.3V	             3.3V Power                      #
##########################################################################################

# Simulate EEPROM with a file
class EEPROM:
    def __init__(self, filename='eeprom.bin', size=1024):
        self.filename = filename
        self.size = size
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                # First byte should indicate amount of tags, set to 0 as default.
                f.write(b'\x00')
                f.write(bytearray([0xFF] * (self.size - 1)))

    def read(self, address):
        with open(self.filename, 'rb') as f:
            f.seek(address)
            data = f.read(1)
            if data:
                return data[0]
            else: 
                return None

    def write(self, address, value):
        with open(self.filename, 'r+b') as f:
            f.seek(address)
            f.write(bytes([value & 0xFF]))

# Handles everything RFID
class RfidHandler():
    def __init__(self):
        self.eeprom = EEPROM('eeprom.bin', 1024)

        self.MAX_IDS = (self.eeprom.size - 6) // 4

        # Initialize RFID reader
        self.MIFAREReader = MFRC522(bus=0, device=0)

        # Set up GPIO numbering
        GPIO.setmode(GPIO.BOARD)  # Use GPIO.BCM if you prefer BCM numbering

        # Global variables
        self.programMode = False
        self.successRead = False
        self.storedCard = [0, 0, 0, 0]
        self.readCard = [0, 0, 0, 0]
        self.masterCard = [0, 0, 0, 0]
    
    def start_rfid_handler(self):
            self.rfid_handler_thread = threading.Thread(target=self.rfid_handler_entry, daemon=True)
            self.rfid_handler_thread.start();
            print("Starting RFID-RC522 handler thread...")

    def getID(self):
        # Make request
        (status, TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)
        if status != self.MIFAREReader.MI_OK:
            return False
        # Avoid multiple chips at once
        (status, uid) = self.MIFAREReader.MFRC522_Anticoll()
        if status != self.MIFAREReader.MI_OK:
            return False
        
        # Successfully read chip!
        self.readCard = uid[0:4] # Store in self.readCard
        print("Scanned PICC's UID:")
        print("%02X %02X %02X %02X" % (self.readCard[0], self.readCard[1], self.readCard[2], self.readCard[3]))
        self.MIFAREReader.MFRC522_SelectTag(uid)
        self.MIFAREReader.MFRC522_StopCrypto1()
        return True

    def isMaster(self, test):
        return test == self.masterCard

    def findIDInEEPROM(self, find):
        count = self.eeprom.read(0)
        # Bounds checking for 'eeprom' size
        if count > self.MAX_IDS or count == 0xFF:
            count = 0
            self.epprom.write(0, 0)
        for i in range(1, count + 1):
            self.readIDFromEEPROM(i)
            if find == self.storedCard:
                return True
        return False

    def readIDFromEEPROM(self, number):
        start = (number * 4) + 2
        self.storedCard = [self.eeprom.read(start + i) for i in range(4)]

    def writeIDToEEPROM(self, a):
        if not self.findIDInEEPROM(a):
            num = self.eeprom.read(0)
            start = (num * 4) + 6
            num += 1
            self.eeprom.write(0, num)
            for j in range(4):
                self.eeprom.write(start + j, a[j])
            #self.successWrite()
            print("Successfully added ID record to EEPROM")
        else:
            #self.failedWrite()
            print("Failed! ID already exists or EEPROM error")

    def deleteIDFromEEPROM(self, a):
        if not self.findIDInEEPROM(a):
            #self.failedWrite()
            print("Failed! ID not found or EEPROM error")
        else:
            num = self.eeprom.read(0)
            slot = self.findIDSlot(a)
            start = (slot * 4) + 2
            looping = ((num - slot) * 4)
            num -= 1
            self.eeprom.write(0, num)
            for j in range(looping):
                self.eeprom.write(start + j, self.eeprom.read(start + 4 + j))
            for k in range(4):
                self.eeprom.write(start + looping + k, 0)
            #self.successDelete()
            print("Successfully removed ID record from EEPROM")

    def findIDSlot(self, find):
        count = self.eeprom.read(0)
        for i in range(1, count + 1):
            self.readIDFromEEPROM(i)
            if find == self.storedCard:
                return i
        return -1

    def rfid_handler_entry(self):
        # Django starts a database connection for each new thread, so we start by closing that.
        connection.close()

        if self.eeprom.read(1) != 143:
            print("No Master Card Defined")
            print("Scan a PICC to Define as Master Card")
            while True:
                successRead = self.getID()
                if successRead:
                    break
            for j in range(4):
                self.eeprom.write(2 + j, self.readCard[j])
            self.eeprom.write(1, 143)
            print("Master Card Defined")

        print("-------------------")
        print("Master Card's UID")
        for i in range(4):
            self.masterCard[i] = self.eeprom.read(2 + i)
            print("%02X" % self.masterCard[i], end='')
        print("\n-------------------")
        print("Everything is ready")
        print("Waiting PICCs to be scanned")

        try:
            while True:
                # Keep reading until chip is read
                successRead = False
                while not successRead:
                    successRead = self.getID()
                    time.sleep(0.5)
    
                # If master chip was read
                if self.programMode:
                    if self.isMaster(self.readCard):
                        print("Master Card Scanned")
                        print("Exiting Program Mode")
                        print("-----------------------------")
                        self.programMode = False
                    else:
                        if self.findIDInEEPROM(self.readCard):
                            print("Known PICC detected, removing...")
                            self.deleteIDFromEEPROM(self.readCard)
                            print("-----------------------------")
                            print("Scan a PICC to ADD or REMOVE to EEPROM")
                        else:
                            print("Unknown PICC detected, adding...")
                            self.writeIDToEEPROM(self.readCard)
                            print("-----------------------------")
                            print("Scan a PICC to ADD or REMOVE to EEPROM")
                else:
                    if self.isMaster(self.readCard):
                        self.programMode = True
                        print("Hello Master - Entered Program Mode")
                        count = self.eeprom.read(0)
                        print(f"I have {count} record(s) on EEPROM")
                        print("Scan a PICC to ADD or REMOVE to EEPROM")
                        print("Scan Master Card again to Exit Program Mode")
                        print("-----------------------------")
                    else:
                        if self.findIDInEEPROM(self.readCard):
                            print("Access Granted")
                            #granted(3)
                        else:
                            print("Access Denied")
                            #denied()
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            GPIO.cleanup()
            sys.exit()
