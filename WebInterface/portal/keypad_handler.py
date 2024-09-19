from django.db import connection

import threading
import time

#import time
import board
import digitalio
import adafruit_matrixkeypad

# Keypad Pins
# (·) F D6
# (·) E D5
# (·) D D21
# (·) B D16
# (·) C D20
# (·) A D12
# (·) G D13
# (·) H D19

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

        self.keys = []
        self.lock = threading.Lock()

    def keypad_handler_entry(self):
        # Django starts a database connection for each new thread, so we start by closing that.
        connection.close()

        previous_keys = []

        while True:
            time.sleep(2)
            with self.lock: 
                # Check for key presses
                current_keys = self.keypad.pressed_keys
                print("Raw from keypad: ", current_keys)
                
                if current_keys and current_keys != previous_keys:
                    # Update keys only if there is a new key press and it's different from the previous state
                    self.keys = current_keys
                    previous_keys = current_keys
                    print("Key Pressed: ", self.keys)
                elif not current_keys:
                    # Optionally retain the last pressed key if no key is currently pressed
                    previous_keys = []  # Clear previous keys if no new input


    def start_keypad_handler(self):
        self.keypad_handler_thread = threading.Thread(target=self.keypad_handler_entry, daemon=True)
        self.keypad_handler_thread.start()
        print("starting keypad handler thread")

