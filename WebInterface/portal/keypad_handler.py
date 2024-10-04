from django.db import connection

import threading
import time
import queue

import RPi.GPIO as GPIO
import digitalio
import adafruit_matrixkeypad

############################
#   Keypad to RPi pinput   #
############################
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
        GPIO.setmode(GPIO.BOARD)

        # Define your row and column pins
        self.rows = [digitalio.DigitalInOut(x) for x in (29, 31, 33, 35)]
        self.cols = [digitalio.DigitalInOut(x) for x in (32, 36, 38, 40)]

        # Define the keys on the keypad
        self.keysMatrix = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        # Initialize the keypad
        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(self.rows, self.cols, self.keysMatrix)
        self.keysQueue = queue.Queue(maxsize=16)

    def keypad_handler_entry(self):
        # Django starts a database connection for each new thread, so we start by closing that.
        connection.close()

        pressed_keys = []

        while True:
            time.sleep(0.1)
            # Check for key presses
            current_keys = self.keypad.pressed_keys
            #print("Raw from keypad: ", current_keys)
            
            if pressed_keys: # Key is held pressed
                if not current_keys: # Key press released
                    # Put the keys pressed into the queue only if there is a new key press 
                    self.keysQueue.put(pressed_keys)
                    # Reset pressed_keys
                    pressed_keys = []

            if current_keys:
                pressed_keys = current_keys

                #print("Key Pressed: ", current_keys)

    def start_keypad_handler(self):
        self.keypad_handler_thread = threading.Thread(target=self.keypad_handler_entry, daemon=True)
        self.keypad_handler_thread.start()
        print("Starting Keypad handler thread...")

