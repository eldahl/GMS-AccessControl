#!/bin/bash
cd /home/pi/GMS-accesscontrol/WebInterface && source WIenv/bin/activate && daphne -b 0.0.0.0 -p 8000 WebInterface.asgi:application
