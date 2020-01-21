"""
    file: ocd_gpio.py
    version: 0.1.0
    author: Adam Mitchell
    brief: Simple Python script to enable full-duplex communication between a Thingpilot module
           and Raspberry Pi via the control of level-shifting ICs
"""

# Standard library imports
import atexit, datetime
from threading import Event

# 3rd-party library imports
import RPi.GPIO as gpio

# GPIO definitions
BOOT0_PIN        = 0
U2_OUTPUT_ENABLE = 16
U3_OUTPUT_ENABLE = 12

# atexit handler
def exit_handler():
    print(f"{datetime.datetime.now()} *** OCD GPIO pin management terminated ***")
    gpio.cleanup()


if __name__ == "__main__":
    print(f"{datetime.datetime.now()} *** OCD GPIO pin management initialising ***")
    
    atexit.register(exit_handler)

    gpio.setmode(gpio.BCM)

    gpio.setup(BOOT0_PIN, gpio.OUT)
    gpio.setup(U2_OUTPUT_ENABLE, gpio.OUT)
    gpio.setup(U3_OUTPUT_ENABLE, gpio.OUT)

    gpio.output(BOOT0_PIN, 0)
    gpio.output(U2_OUTPUT_ENABLE, 1)
    gpio.output(U3_OUTPUT_ENABLE, 1)

    print(f"{datetime.datetime.now()} *** OCD GPIO pin management ready ***")

    # If we terminate the script via Ctrl + C
    try:
        Event().wait()
    except KeyboardInterrupt:
        print(f"{datetime.datetime.now()} *** OCD GPIO pin management terminating ***")