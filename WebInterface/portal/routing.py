from django.urls import path
from .consumers import KeypadConsumer

websocket_urlpatterns = [
        path('ws/keypad/', KeypadConsumer.as_asgi()),
]
