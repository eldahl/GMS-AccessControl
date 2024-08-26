import RPi.GPIO as GPIO
import time
import spidev
import MFRC522
import signal
import sys

# Pin configuration
redLed = 7
greenLed = 6
blueLed = 5
relay = 4
wipeB = 3

# Define LED states
LED_ON = GPIO.LOW
LED_OFF = GPIO.HIGH

# Initialize RFID
MIFAREReader = MFRC522.MFRC522()

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(redLed, GPIO.OUT)
GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(blueLed, GPIO.OUT)
GPIO.setup(wipeB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, GPIO.HIGH)
GPIO.output(redLed, LED_OFF)
GPIO.output(greenLed, LED_OFF)
GPIO.output(blueLed, LED_OFF)

# Variables
programMode = False
successRead = False
storedCard = [0, 0, 0, 0]
readCard = [0, 0, 0, 0]
masterCard = [0, 0, 0, 0]

# Interrupt
def end_read(signal, frame):
    print("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    sys.exit()

signal.signal(signal.SIGINT, end_read)

# Function to read an ID from EEPROM
def readID(number):
    start = (number * 4) + 2
    for i in range(4):
        storedCard[i] = EEPROM.read(start + i)

# Function to write an ID to EEPROM
def writeID(a):
    if not findID(a):
        num = EEPROM.read(0)
        start = (num * 4) + 6
        num += 1
        EEPROM.write(0, num)
        for j in range(4):
            EEPROM.write(start + j, a[j])
        successWrite()
        print("Successfully added ID record to EEPROM")
    else:
        failedWrite()
        print("Failed! There is something wrong with ID or bad EEPROM")

# Function to delete an ID from EEPROM
def deleteID(a):
    if not findID(a):
        failedWrite()
        print("Failed! There is something wrong with ID or bad EEPROM")
    else:
        num = EEPROM.read(0)
        slot = findIDSLOT(a)
        start = (slot * 4) + 2
        looping = ((num - slot) * 4)
        num -= 1
        EEPROM.write(0, num)
        for j in range(looping):
            EEPROM.write(start + j, EEPROM.read(start + 4 + j))
        for k in range(4):
            EEPROM.write(start + j + k, 0)
        successDelete()
        print("Successfully removed ID record from EEPROM")

# Function to check two byte arrays
def checkTwo(a, b):
    for k in range(4):
        if a[k] != b[k]:
            return False
    return True

# Function to find the slot of an ID in EEPROM
def findIDSLOT(find):
    count = EEPROM.read(0)
    for i in range(1, count + 1):
        readID(i)
        if checkTwo(find, storedCard):
            return i
    return None

# Function to find an ID in EEPROM
def findID(find):
    count = EEPROM.read(0)
    for i in range(1, count + 1):
        readID(i)
        if checkTwo(find, storedCard):
            return True
    return False

# Function to handle successful write to EEPROM
def successWrite():
    for _ in range(3):
        GPIO.output(greenLed, LED_ON)
        time.sleep(0.2)
        GPIO.output(greenLed, LED_OFF)
        time.sleep(0.2)

# Function to handle failed write to EEPROM
def failedWrite():
    for _ in range(3):
        GPIO.output(redLed, LED_ON)
        time.sleep(0.2)
        GPIO.output(redLed, LED_OFF)
        time.sleep(0.2)

# Function to handle successful delete from EEPROM
def successDelete():
    for _ in range(3):
        GPIO.output(blueLed, LED_ON)
        time.sleep(0.2)
        GPIO.output(blueLed, LED_OFF)
        time.sleep(0.2)

# Function to handle granted access
def granted(setDelay):
    GPIO.output(blueLed, LED_OFF)
    GPIO.output(redLed, LED_OFF)
    GPIO.output(greenLed, LED_ON)
    time.sleep(setDelay / 1000)
    GPIO.output(greenLed, LED_OFF)

# Function to handle denied access
def denied():
    GPIO.output(greenLed, LED_OFF)
    GPIO.output(blueLed, LED_OFF)
    GPIO.output(redLed, LED_ON)
    time.sleep(1)
    GPIO.output(redLed, LED_OFF)

# Function to check if the card is a master card
def isMaster(test):
    return checkTwo(test, masterCard)

# Function to cycle LEDs in program mode
def cycleLeds():
    while programMode:
        GPIO.output(redLed, LED_OFF)
        GPIO.output(greenLed, LED_ON)
        GPIO.output(blueLed, LED_OFF)
        time.sleep(0.2)
        GPIO.output(redLed, LED_OFF)
        GPIO.output(greenLed, LED_OFF)
        GPIO.output(blueLed, LED_ON)
        time.sleep(0.2)
        GPIO.output(redLed, LED_ON)
        GPIO.output(greenLed, LED_OFF)
        GPIO.output(blueLed, LED_OFF)
        time.sleep(0.2)

# Function to turn on normal mode LEDs
def normalModeOn():
    GPIO.output(blueLed, LED_ON)
    GPIO.output(redLed, LED_OFF)
    GPIO.output(greenLed, LED_OFF)
    GPIO.output(relay, GPIO.HIGH)

# Function to monitor wipe button
def monitorWipeButton(interval):
    start = time.time()
    while time.time() - start < interval:
        if GPIO.input(wipeB) != GPIO.LOW:
            return False
        time.sleep(0.1)
    return True

# EEPROM mock functions (replace with actual EEPROM handling code)
class EEPROM:
    @staticmethod
    def read(address):
        # Replace with actual EEPROM read logic
        return 0

    @staticmethod
    def write(address, value):
        # Replace with actual EEPROM write logic
        pass

# Main loop
while True:
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            readCard = uid[:4]
            print("Card read UID: %s" % readCard)

            if isMaster(readCard):
                programMode = not programMode
                print("Master card detected, toggling program mode to %s" % programMode)
                if programMode:
                    cycleLeds()
                else:
                    normalModeOn()
            else:
                if programMode:
                    if findID(readCard):
                        deleteID(readCard)
                        print("Known card deleted")
                    else:
                        writeID(readCard)
                        print("Unknown card added")
                else:
                    if findID(readCard):
                        granted(300)
                    else:
                        denied()

    time.sleep(0.1)

