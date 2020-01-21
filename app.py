"""
    file:    app.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Flask webserver with real-time functionality provided by SocketIO and eventlet
"""

# Standard library imports
from os import urandom

# 3rd-party library imports
import eventlet
from flask import Flask, render_template, escape, request
from flask_socketio import SocketIO

# Thingpilot library imports
import app_utils

# Global Flask and SocketIO objects
app = Flask(__name__)
app.config['SECRET_KEY'] = f"{urandom(64)}"
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def hello():
    return render_template("home.html")


if __name__ == '__main__':
    socketio.run(app, host=app_utils.get_ip_address(), port=80, debug=True)