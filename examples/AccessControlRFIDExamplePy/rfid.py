import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal
import time
import sys
import os
import traceback

# Set up GPIO numbering
GPIO.setmode(GPIO.BOARD)  # Use GPIO.BCM if you prefer BCM numbering

RST_PIN = 22

# Global variables
programMode = False
successRead = False
storedCard = [0, 0, 0, 0]
readCard = [0, 0, 0, 0]
masterCard = [0, 0, 0, 0]

# Simulate EEPROM with a file
class EEPROM:
    def __init__(self, filename='eeprom.bin', size=1024):
        self.filename = filename
        self.size = size
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                # First byte should indicate amount of tags, set to 0 as default.
                f.write(0)
                f.write(bytearray([0xFF] * self.size - 1))

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

eeprom = EEPROM('eeprom.bin', 1024)

MAX_IDS = (eeprom.size - 6) // 4

# Initialize RFID reader
MIFAREReader = MFRC522(bus=0, device=0)

def monitorWipeButton(interval):
    start_time = time.time()
    while (time.time() - start_time) < interval:
        time.sleep(0.1)
    return True

def getID():
    global readCard
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status != MIFAREReader.MI_OK:
        return False
    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    if status != MIFAREReader.MI_OK:
        return False
    print("Scanned PICC's UID:")
    readCard = uid[0:4]
    print("%02X%02X%02X%02X" % (readCard[0], readCard[1], readCard[2], readCard[3]))
    MIFAREReader.MFRC522_SelectTag(uid)
    MIFAREReader.MFRC522_StopCrypto1()
    return True

def isMaster(test):
    return checkTwo(test, masterCard)

def checkTwo(a, b):
    return a == b

def findID(find):
    count = eeprom.read(0)
    # Bounds checking for 'eeprom' size
    if count > MAX_IDS or count == 0xFF:
        count = 0
        epprom.write(0, 0)
    for i in range(1, count + 1):
        readID(i)
        if checkTwo(find, storedCard):
            return True
    return False

def readID(number):
    global storedCard
    start = (number * 4) + 2
    storedCard = [eeprom.read(start + i) for i in range(4)]

def writeID(a):
    if not findID(a):
        num = eeprom.read(0)
        start = (num * 4) + 6
        num += 1
        eeprom.write(0, num)
        for j in range(4):
            eeprom.write(start + j, a[j])
        successWrite()
        print("Successfully added ID record to EEPROM")
    else:
        failedWrite()
        print("Failed! ID already exists or EEPROM error")

def deleteID(a):
    if not findID(a):
        failedWrite()
        print("Failed! ID not found or EEPROM error")
    else:
        num = eeprom.read(0)
        slot = findIDSLOT(a)
        start = (slot * 4) + 2
        looping = ((num - slot) * 4)
        num -= 1
        eeprom.write(0, num)
        for j in range(looping):
            eeprom.write(start + j, eeprom.read(start + 4 + j))
        for k in range(4):
            eeprom.write(start + looping + k, 0)
        successDelete()
        print("Successfully removed ID record from EEPROM")

def findIDSLOT(find):
    count = eeprom.read(0)
    for i in range(1, count + 1):
        readID(i)
        if checkTwo(find, storedCard):
            return i
    return -1

def successWrite():
    pass

def failedWrite():
    pass

def successDelete():
    pass

def granted(setDelay):
    pass

def denied():
    pass

def normalModeOn():
    pass

def cycleLeds():
    pass

# Initialization code
#if GPIO.input(WIPE_BUTTON_PIN) == GPIO.LOW:
#    GPIO.output(RED_LED_PIN, GPIO.HIGH)
#    print("Wipe Button Pressed")
#    print("You have 10 seconds to Cancel")
#    print("This will remove all records and cannot be undone")
#    buttonState = monitorWipeButton(10)
#    if buttonState and GPIO.input(WIPE_BUTTON_PIN) == GPIO.LOW:
#        print("Starting Wiping EEPROM")
#        for x in range(1024):
#            eeprom.write(x, 0)
#        print("EEPROM Successfully Wiped")
#        for _ in range(3):
#            GPIO.output(RED_LED_PIN, GPIO.LOW)
#            time.sleep(0.2)
#            GPIO.output(RED_LED_PIN, GPIO.HIGH)
#            time.sleep(0.2)
#        GPIO.output(RED_LED_PIN, GPIO.LOW)
#    else:
#        print("Wiping Cancelled")
#        GPIO.output(RED_LED_PIN, GPIO.LOW)

if eeprom.read(1) != 143:
    print("No Master Card Defined")
    print("Scan a PICC to Define as Master Card")
    while True:
        successRead = getID()
        if successRead:
            break
    for j in range(4):
        eeprom.write(2 + j, readCard[j])
    eeprom.write(1, 143)
    print("Master Card Defined")

print("-------------------")
print("Master Card's UID")
for i in range(4):
    masterCard[i] = eeprom.read(2 + i)
    print("%02X" % masterCard[i], end='')
print("\n-------------------")
print("Everything is ready")
print("Waiting PICCs to be scanned")
cycleLeds()

try:
    while True:
        successRead = False
        while not successRead:
            successRead = getID()
            if programMode:
                cycleLeds()
            else:
                normalModeOn()
            time.sleep(0.5)
            #if GPIO.input(WIPE_BUTTON_PIN) == GPIO.LOW:
               # print("Wipe Button Pressed")
               # print("Master Card will be Erased! in 10 seconds")
               # buttonState = monitorWipeButton(10)
                #if buttonState and GPIO.input(WIPE_BUTTON_PIN) == GPIO.LOW:
                #    eeprom.write(1, 0)
                #    print("Master Card Erased from device")
                #    print("Please reset to re-program Master Card")
                #    sys.exit()
                #else:
                #    print("Master Card Erase Cancelled")
        if programMode:
            if isMaster(readCard):
                print("Master Card Scanned")
                print("Exiting Program Mode")
                print("-----------------------------")
                programMode = False
            else:
                if findID(readCard):
                    print("Known PICC detected, removing...")
                    deleteID(readCard)
                    print("-----------------------------")
                    print("Scan a PICC to ADD or REMOVE to EEPROM")
                else:
                    print("Unknown PICC detected, adding...")
                    writeID(readCard)
                    print("-----------------------------")
                    print("Scan a PICC to ADD or REMOVE to EEPROM")
        else:
            if isMaster(readCard):
                programMode = True
                print("Hello Master - Entered Program Mode")
                count = eeprom.read(0)
                print(f"I have {count} record(s) on EEPROM")
                print("Scan a PICC to ADD or REMOVE to EEPROM")
                print("Scan Master Card again to Exit Program Mode")
                print("-----------------------------")
            else:
                if findID(readCard):
                    print("Access Granted")
                    granted(3)
                else:
                    print("Access Denied")
                    denied()
except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    GPIO.cleanup()
    sys.exit()
