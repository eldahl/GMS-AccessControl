# GMS AcessControl Web Interface

# Install
Setup python virtual environment:	
Run `python -m venv WIenv` from the same directory as this readme.

Activate virtual environment:
`source WIenv/bin/activate`

Install Django:
`pip install django`.

Install Daphne:
`pip install daphne`

Install Channels:
`pip install channels`

# Usage
Follow Django usage patterns, by running commands with `python manage.py`.
Run development server with `daphne -b 0.0.0.0 -p 8000 WebInterface.asgi:application` 

