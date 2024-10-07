import signal
import time
import os
import queue
import board
import digitalio
import adafruit_matrixkeypad
import traceback
import sys
import threading
import RPi.GPIO as GPIO

from mfrc522 import MFRC522
from django.db import connection
from django.apps import apps

class Coordinator():
    
    def __init__(self):
        # Set board pin configuration before both projects start
        # IMPORTANT!!
        # We need both handlers to cooperate their pin usage!!
        gpioMode = GPIO.getmode()
        if gpioMode is None:
            GPIO.setmode(GPIO.BOARD)

        self.keypad_handler = KeypadHandler()
        self.rfid_handler = RfidHandler()
        
        self.coordinator_thread = threading.Thread(target=self.coordinator_entry, daemon=True)
        self.coordinator_thread.start()
        print("Started Coordinator thread...")

    def coordinator_entry(self):
        
        while True:
            if apps.ready:
                break

        while True:
            (successRead, chipId) = self.rfid_handler.CheckForAccess()

            if successRead:
                # Add to log
                from .models import LogEntry
                entry = LogEntry(event="RFIDEvent", message="Scanned Chip ID: {}".format(chipId))
                entry.save()
                
                from .models import UserWithAccess

                # Get users and look for a match
                users = UsersWithAccess.objects.all()
                foundUser = None
                for u in users:
                    if u.chip_indentifier == chipId:
                        foundUser = u
                
                # If unknown card, show access denied
                if foundUser == None:
                    # Add to log
                    unknownUserLogEntry = LogEntry(event="RFIDEvent", message="Unknown chip!")
                    unknownUserLogEntry.save()
                    
                    # TODO: SHOW ACCESS DENIED
                
                # If known card, initiate code checking
                else:
                    knownUserLogEntry = LogEntry(event="RFIDEvent", message="Known user: {} {} Phone: {}".format(foundUser.first_name, foundUser.last_name, foundUser.phone))
                    knownUserLogEntry.save()

                    try:
                        while True:
                            self.keypad_handler.CheckForInput()
                            if self.keypad_handler.keysQueue.qsize == 4:
                                print(list(self.keypad_handler.keysQueue))

                    except Exception as e:
                        print(f"An error occurred: {e}")
                        traceback.print_exc()
                        print("FATAL: Coordinator no longer running.")
                        sys.exit


############################
#   Keypad to RPi pinput   #
###########################################
# [Keypad Pins] [RPi BCM(GPIO)] [RPi Pin] #
#    (·) F            6             31    #
#    (·) E            5             29    #
#    (·) D            21            40    #
#    (·) B            16            36    #
#    (·) C            20            38    #
#    (·) A            12            32    #
#    (·) G            13            33    #
#    (·) H            19            35    #
###########################################
class KeypadHandler():

    def __init__(self):
        # Define your row and column pins
        self.rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
        self.cols = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20, board.D21)]
        
        # Define the keys on the keypad
        self.keysMatrix = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        # Initialize the keypad
        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(self.rows, self.cols, self.keysMatrix)
        
        # Store keys
        self.keysQueue = queue.Queue(maxsize=4)

        # Keep track of pressed keys
        self.pressed_keys = []

    def CheckForInput(self):
        time.sleep(0.1)

        # Check for key presses
        current_keys = self.keypad.pressed_keys
        
        #print("Raw from keypad: ", current_keys)
        
        # If we have a current key held down
        if self.pressed_keys: # Key is held pressed
            if not current_keys: # Key press released
                # Put keys in queue
                self.keysQueue.put(self.pressed_keys)

                # Reset pressed_keys
                self.pressed_keys = []
        
        # If new key is pressed
        if current_keys:
            self.pressed_keys = current_keys
            #print("Key Pressed: ", current_keys)


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
class RfidHandler():
    def __init__(self):
        self.eeprom = EEPROM('eeprom.bin', 1024)

        self.MAX_IDS = (self.eeprom.size - 6) // 4
        
        # Initialize RFID reader
        self.MIFAREReader = MFRC522(bus=0, device=0)

        # Global variables
        self.programMode = False
        self.successRead = False
        self.storedCard = [0, 0, 0, 0]
        self.readCard = [0, 0, 0, 0]
        self.masterCard = [0, 0, 0, 0]

        self.setup_mastercard()
    
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

#    def isMaster(self, test):
#        return test == self.masterCard

#    def findIDInEEPROM(self, find):
#        count = self.eeprom.read(0)
#        # Bounds checking for 'eeprom' size
#        if count > self.MAX_IDS or count == 0xFF:
#            count = 0
#            self.epprom.write(0, 0)
#        for i in range(1, count + 1):
#            self.readIDFromEEPROM(i)
#            if find == self.storedCard:
#                return True
#        return False

#    def readIDFromEEPROM(self, number):
#        start = (number * 4) + 2
#        self.storedCard = [self.eeprom.read(start + i) for i in range(4)]

#    def writeIDToEEPROM(self, a):
#        if not self.findIDInEEPROM(a):
#            num = self.eeprom.read(0)
#            start = (num * 4) + 6
#            num += 1
#            self.eeprom.write(0, num)
#            for j in range(4):
#                self.eeprom.write(start + j, a[j])
#            #self.successWrite()
#            print("Successfully added ID record to EEPROM")
#        else:
#            #self.failedWrite()
#            print("Failed! ID already exists or EEPROM error")

#    def deleteIDFromEEPROM(self, a):
#        if not self.findIDInEEPROM(a):
#            #self.failedWrite()
#            print("Failed! ID not found or EEPROM error")
#        else:
#            num = self.eeprom.read(0)
#            slot = self.findIDSlot(a)
#            start = (slot * 4) + 2
#            looping = ((num - slot) * 4)
#            num -= 1
#            self.eeprom.write(0, num)
#            for j in range(looping):
#                self.eeprom.write(start + j, self.eeprom.read(start + 4 + j))
#            for k in range(4):
#                self.eeprom.write(start + looping + k, 0)
#            #self.successDelete()
#            print("Successfully removed ID record from EEPROM")

#    def findIDSlot(self, find):
#        count = self.eeprom.read(0)
#        for i in range(1, count + 1):
#            self.readIDFromEEPROM(i)
#            if find == self.storedCard:
#                return i
#        return -1
    
    def setup_mastercard(self):
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

    def CheckForAccess(self):
        try:
            successRead = self.getID()
            return (successRead, self.readCard);

        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            GPIO.cleanup()
            sys.exit()
#            while True:
#                # Keep reading until chip is read
#                successRead = False
#                while not successRead:
#                    successRead = self.getID()
#                    time.sleep(0.5)
#    
#                # If master chip was read
#                if self.programMode:
#                    if self.isMaster(self.readCard):
#                        print("Master Card Scanned")
#                        print("Exiting Program Mode")
#                        print("-----------------------------")
#                        self.programMode = False
#                    else:
#                        if self.findIDInEEPROM(self.readCard):
#                            print("Known PICC detected, removing...")
#                            self.deleteIDFromEEPROM(self.readCard)
#                            print("-----------------------------")
#                            print("Scan a PICC to ADD or REMOVE to EEPROM")
#                        else:
#                            print("Unknown PICC detected, adding...")
#                            self.writeIDToEEPROM(self.readCard)
#                            print("-----------------------------")
#                            print("Scan a PICC to ADD or REMOVE to EEPROM")
#                else:
#                    if self.isMaster(self.readCard):
#                        self.programMode = True
#                        print("Hello Master - Entered Program Mode")
#                        count = self.eeprom.read(0)
#                        print(f"I have {count} record(s) on EEPROM")
#                        print("Scan a PICC to ADD or REMOVE to EEPROM")
#                        print("Scan Master Card again to Exit Program Mode")
#                        print("-----------------------------")
#                    else:
#                        if self.findIDInEEPROM(self.readCard):
#                            print("Access Granted")
#                            #granted(3)
#                        else:
#                            print("Access Denied")
#                            #denied()
#        except KeyboardInterrupt:
#            GPIO.cleanup()
#            sys.exit()
#        except Exception as e:
#            print(f"An error occurred: {e}")
#            traceback.print_exc()
#            GPIO.cleanup()
#            sys.exit()


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

