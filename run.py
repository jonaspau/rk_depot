#!/usr/bin/env python
"""
Device Booking System - Main Application Entry Point
"""

from app import create_app
from flask import redirect, url_for
import os

app = create_app()


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
