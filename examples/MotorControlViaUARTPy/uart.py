import serial
import threading

serialport = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3.0)

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return

def my_callback(inp):
    if inp == 'o':
        serialport.write(b'o')
    elif inp == 'i':
        serialport.write(b'i')

#start the Keyboard thread
kthread = KeyboardThread(my_callback)

while True:
    rcv = serialport.read(80)
    print(repr(rcv))
