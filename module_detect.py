"""
    file:    module_detect.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Detect the presence of a Thingpilot module and alert webserver using SocketIO
"""

# Standard library imports
import atexit, datetime, time

# 3rd-party library imports
import RPi.GPIO as gpio
import socketio

# Thingpilot library imports
import app_utils

# GPIO definitions
DETECT_PIN = 1

# Global SocketIO object
sio = socketio.Client()


def exit_handler():
    gpio.cleanup()


@sio.on('IS_MODULE_PRESENT')
def is_module_present(data):
    state = gpio.input(DETECT_PIN)

    if(state == 1):
        print(f"{datetime.datetime.now()} module_detect.py: Module connected, triggered by JS")
        sio.emit('MODULE_PRESENT')
    else:
        print(f"{datetime.datetime.now()} module_detect.py: Module disconnected, triggered by JS")
        sio.emit('MODULE_NOT_PRESENT')


if __name__ == "__main__":
    sio.connect(f"http://{app_utils.get_ip_address()}:80")

    atexit.register(exit_handler)

    gpio.setmode(gpio.BCM)

    gpio.setup(DETECT_PIN, gpio.IN)

    current_state = 0
    previous_state = 0

    try:
        while True:
            previous_state = current_state
            current_state = gpio.input(DETECT_PIN)

            if(current_state == 1 and previous_state == 0):
                    print(f"{datetime.datetime.now()} module_detect.py: Module connected")
                    sio.emit('MODULE_PRESENT')         
            elif(current_state == 0 and previous_state == 1):
                    print(f"{datetime.datetime.now()} module_detect.py:  Module disconnected")
                    sio.emit('MODULE_NOT_PRESENT')

            time.sleep(0.15)       
    except KeyboardInterrupt:
        pass