import traceback
import sys
import threading

from .keypad_handler import KeypadHandler
from .rfid_handler import RfidHandler

class Coordinator():
    
    def __init__(self):
        self.keypad_handler = KeypadHandler()
        #self.rfid_handler = RfidHandler()

        self.keypad_handler.start_keypad_handler()
        #self.rfid_handler.start_rfid_handler()
    
    def start_coordinator(self):
        self.coordinator_thread = threading.Thread(target=self.coordinator_loop, daemon=True)
        self.coordinator_thread.start()
        print("Started Coordinator thread...")

    def coordinator_loop(self):
        try:
            while True:
                if not self.keypad_handler.keysQueue.empty():
                    key = self.keypad_handler.keysQueue.get()
                    print(f"Got key: {key}")
                    self.keypad_handler.keysQueue.task_done()

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            print("FATAL: Coordinator no longer running.")
            sys.exit
