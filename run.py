#!/usr/bin/env python
"""
Device Booking System - Main Application Entry Point
"""

from pathlib import Path
from dotenv import load_dotenv

from app import create_app
from flask import redirect, url_for
import os


dotenv_path = Path(__file__).resolve().with_name('.env')
if not dotenv_path.exists():
    raise RuntimeError(
        "Missing .env file. Create one from .env.example (cp .env.example .env) "
        "and set SECRET_KEY, etc."
    )
load_dotenv(dotenv_path)

app = create_app()


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
