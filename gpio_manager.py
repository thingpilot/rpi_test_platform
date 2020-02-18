"""
    file:    gpio_manager.py
    version: 0.2.0
    author:  Adam Mitchell
    brief:   Detect the presence of a Thingpilot module and alert webserver using SocketIO and 
             manage GPIOs that control hardware necessary for communications with module
"""

# Standard library imports
import atexit, datetime, sys, time
from subprocess import check_output

# 3rd-party library imports
import RPi.GPIO as gpio
import socketio


sio = socketio.Client()


class GPIOManager(object):
    DETECT_PIN       = 1
    BOOT0_PIN        = 0
    U2_OUTPUT_ENABLE = 16
    U3_OUTPUT_ENABLE = 12
    
    def __init__(self):
        self.current_state = 0
        self.previous_state = 0

        gpio.setmode(gpio.BCM)

        gpio.setup(GPIOManager.DETECT_PIN,       gpio.IN)
        gpio.setup(GPIOManager.BOOT0_PIN,        gpio.OUT, initial=0)
        gpio.setup(GPIOManager.U2_OUTPUT_ENABLE, gpio.OUT, initial=1)
        gpio.setup(GPIOManager.U3_OUTPUT_ENABLE, gpio.OUT, initial=1)

    def __delattr__(self):
        self._cleanup_gpio()

    def _cleanup_gpio(self):
        gpio.cleanup()

    def is_connected(self):
        return self.current_state

    def poll(self):
        while True:
            self.previous_state = self.current_state
            self.current_state = gpio.input(GPIOManager.DETECT_PIN)

            if(self.current_state == 1 and self.previous_state == 0):
                print(f"{datetime.datetime.now()} gpio_manager.py: Module connected")
                sio.emit('is_connected_progress', True, namespace='/GPIONamespace')         
            elif(self.current_state == 0 and self.previous_state == 1):
                print(f"{datetime.datetime.now()} gpio_manager.py: Module disconnected")
                sio.emit('is_connected_progress', False, namespace='/GPIONamespace') 

            sio.sleep(0.15)   


class GPIOManagerNamespace(socketio.ClientNamespace):
    def __init__(self, gpio_man, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sio_connected = False

        self._gpio_manager = gpio_man

    def on_connect(self):
        self.sio_connected = True
        
        sio.start_background_task(self._gpio_manager.poll)

    def on_disconnect(self):
        self.sio_connected = False

    def on_is_connected(self, data):
        is_connected = self._gpio_manager.is_connected()

        if is_connected:
            print(f"{datetime.datetime.now()} gpio_manager.py: Module connected, triggered by JS")
        else:
            print(f"{datetime.datetime.now()} gpio_manager.py: Module disconnected, triggered by JS")

        sio.emit('is_connected_progress', is_connected, namespace='/GPIONamespace')


def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


def connect(n_attempts=100):
    ns = GPIOManagerNamespace(GPIOManager(), '/GPIOManagerNamespace')
    sio.register_namespace(ns)

    for i in range(n_attempts):
        print(f"{datetime.datetime.now()} gpio_manager.py: Attempt {i + 1} connecting to {get_ip_address()}:80")

        try:
            sio.connect(f'http://{get_ip_address()}:80')       

            print(f"{datetime.datetime.now()} gpio_manager.py: Connected to {get_ip_address()}:80")

            break
        except socketio.exceptions.ConnectionError:
            sio.sleep(0.5)

    if ns.sio_connected:
        sio.sleep(10)

    sio.sleep(1)

    return ns.sio_connected


if __name__ == "__main__":
    if connect():
        while True:
            sio.sleep(1)
    else:
        print(f"{datetime.datetime.now()} gpio_manager.py: Failed to connect to {get_ip_address()}:80")