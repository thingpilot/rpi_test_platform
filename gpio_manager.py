"""
    file:    gpio_manager.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Detect the presence of a Thingpilot module and alert webserver using SocketIO and 
             manage GPIOs that control hardware necessary for communications with module
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

BOOT0_PIN        = 0
U2_OUTPUT_ENABLE = 16
U3_OUTPUT_ENABLE = 12

# Global SocketIO object
sio = socketio.Client()


def exit_handler():
    gpio.cleanup()
    print(f"{datetime.datetime.now()} gpio_manager.py: Terminating GPIO pin management interface")


@sio.on('IS_MODULE_PRESENT')
def is_module_present(data):
    state = gpio.input(DETECT_PIN)

    if(state == 1):
        print(f"{datetime.datetime.now()} gpio_manager.py: Module connected, triggered by JS")
        sio.emit('MODULE_PRESENT')
    else:
        print(f"{datetime.datetime.now()} gpio_manager.py: Module disconnected, triggered by JS")
        sio.emit('MODULE_NOT_PRESENT')


@sio.on('SHUTDOWN')
def handle_shutdown():
    exit_handler()


if __name__ == "__main__":
    atexit.register(exit_handler)
    connected = False

    print(f"{datetime.datetime.now()} gpio_manager.py: Intialising GPIO pin management interface")

    for i in range(1, 10):
        print(f"{datetime.datetime.now()} gpio_manager.py: Attempt {i} connecting to {app_utils.get_ip_address()}:80")
        
        try:    
            sio.connect(f"http://{app_utils.get_ip_address()}:80")
            connected = True
            break
        except socketio.exceptions.ConnectionError:
            time.sleep(1)

    if connected:

        gpio.setmode(gpio.BCM)

        gpio.setup(DETECT_PIN, gpio.IN)
        gpio.setup(BOOT0_PIN, gpio.OUT, initial=0)
        gpio.setup(U2_OUTPUT_ENABLE, gpio.OUT, initial=1)
        gpio.setup(U3_OUTPUT_ENABLE, gpio.OUT, initial=1)

        current_state = 0
        previous_state = 0

        print(f"{datetime.datetime.now()} gpio_manager.py: GPIO pin management interface ready")

        try:
            while True:
                previous_state = current_state
                current_state = gpio.input(DETECT_PIN)

                if(current_state == 1 and previous_state == 0):
                        print(f"{datetime.datetime.now()} gpio_manager.py: Module connected")
                        sio.emit('MODULE_PRESENT')         
                elif(current_state == 0 and previous_state == 1):
                        print(f"{datetime.datetime.now()} gpio_manager.py: Module disconnected")
                        sio.emit('MODULE_NOT_PRESENT')

                time.sleep(0.15)       
        except KeyboardInterrupt:
            pass
    
    else:
        print(f"{datetime.datetime.now()} gpio_manager.py: Failed to connect to {app_utils.get_ip_address()}:80. Server is down?")