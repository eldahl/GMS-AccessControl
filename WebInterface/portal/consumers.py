from channels.generic.websocket import AsyncWebsocketConsumer
import json
import time
from . import apps


class KeypadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if not apps.keypad_handler:
            print("no lock handler")
            return

        with apps.keypad_handler.lock:
            keys_copy = apps.keypad_handler.keys.copy();
            print("keys from lock: ", apps.keypad_handler.keys);

        print("keys copy", keys_copy);

        await self.send(text_data=json.dumps({
            'keys': keys_copy
        })) 
