import time
import board
import digitalio
import adafruit_matrixkeypad

# Define your row and column pins
rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
cols = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20, board.D21)]

# Define the keys on the keypad
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Initialize the keypad
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

while True:
    # Check for key presses
    keys = keypad.pressed_keys
    if keys:
        # Print the keys pressed to the serial log
        print("Key Pressed: ", keys)

    time.sleep(0.1)
