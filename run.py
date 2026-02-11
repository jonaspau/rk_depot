#!/usr/bin/env python
"""
Device Booking System - Main Application Entry Point
"""
from app import create_app
from flask import redirect, url_for

if __name__ == '__main__':
    app = create_app()
    @app.route('/')
    def homepage():
        return redirect(url_for('user.user_dashboard'))

    print("Starting Device Booking System...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("Admin Dashboard: http://localhost:5000/admin")
    print("User Dashboard: http://localhost:5000/user")
    print("Device Status: http://localhost:5000/status")
    print("Activity Log: http://localhost:5000/log")
    print("\nPress Ctrl+C to stop the server")
    app.run(debug=True, host='localhost', port=5000)
