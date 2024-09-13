from channels.generic.websocket import AsyncWebsocketConsumer
import json

class KeypadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'test'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'message:': 'Hello from portal'
        })) 
