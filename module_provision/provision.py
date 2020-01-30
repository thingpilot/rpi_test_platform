"""
    file:    provision.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Handles device provisioning and setup with the ThingPilot backend
"""

"""
    file:    hardware_test.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python script to verify Wright/Earhart module hardware functionality. This will test
             that all available GPIO pins function correctly as well as all available comms busses,
             including I2C, SPI and UART.
"""

# Standard library imports
import functools
import time
from datetime import datetime

# 3rd-party library imports
import serial


class ThingpilotProvisioner():
    EARHART = 'earhart'
    WRIGHT = 'wright'

    ACK = 'OK'
    PROV_INIT = 'AT+MODPROV'
    PROV_END = 'AT+ENDPROV'

    def __init__(self, module, uid):
        self.module = module
        self.uid = uid

        self.uart = None
        self.timeout_flag = False
        self.test_passed = True
        self.total_prov_start_time = self._get_millis()

    def _reset_timeout_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.timeout_flag = False

            return func(self, *args, **kwargs)

        return wrap

    def _flush_uart_input_buffer(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            if self.uart is not None:
                self.uart.reset_input_buffer()

            return func(self, *args, **kwargs)

        return wrap

    def _get_millis(self):
        return int(round(time.time() * 1000))

    def start_provision(self):
        date_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
        return { 'success': True, 'message': f'*** Beginning {self.module.title()} provisioning at: {date_time} ***\n' }

    @_reset_timeout_flag
    def initialise_device(self):
        try:
            self.uart = serial.Serial('/dev/serial0', 9600, timeout=0.2)
        except serial.serialutil.SerialException:
            return { 'success': False, 'message': '    Provision (init) - Failed to connect to port /dev/serial0\n'}

        if not self.uart.is_open:
            self.uart.open()

        if not self.uart.is_open:
            return { 'success': False, 'message': '    Provision (init) - Failed to open port /dev/serial0\n'}

        start_time = self._get_millis()

        while True:
            s = str(self.uart.readline())
            print(f"{datetime.now()} provision.py: ({self.module.title()}) received: {s}")

            if ThingpilotProvisioner.PROV_INIT in s:
                self.uart.write(bytes(ThingpilotProvisioner.ACK, 'utf-8'))
                print(f"{datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.ACK}")
                break

            if self._get_millis() > (start_time + 1000):
                self.timeout_flag = True
                break
        
        if self.timeout_flag:
            return { 'success': False, 'message': '    Provision (init) - Failed to place module into provisioning mode\n'}
                    
        return { 'success': True, 'message': '    Provision (init) - Module successfully placed into provisioning mode\n'}

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def provision_device(self):
        pass

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def end_provision(self):
        start_time = self._get_millis()

        while True:
            self.uart.write(bytes(ThingpilotProvisioner.PROV_END, 'utf-8'))
            print(f"{datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.PROV_END}")

            s = str(self.uart.readline())
            print(f"{datetime.now()} provision.py: ({self.module.title()}) received: {s}")

            if 'PROV COMPLETE' in s:
                break

            if self._get_millis() > (start_time + 1000):
                break

        if self.uart.is_open:
            self.uart.close()

        if self.test_passed:
            result_string = 'PROVISIONED <i class="fas fa-check-circle"></i>'
        else:
            result_string = 'FAILED <i class="fas fa-times-circle"></i>'

        total_prov_time_taken = self._get_millis() - self.total_prov_start_time

        return { 'success': True, 'message': f'*** Ended {self.module.title()} provisioning. Took: {total_prov_time_taken}ms ***\n    Provisioning - {result_string}\n' }

    def provision(self):
        steps = { 
            'start_provision': 'self.start_provision()',
            'initialise_device': 'self.initialise_device()',
            'provision_device': 'self.provision_device()',
            'end_provision': 'self.end_provision()'
        }

        for step, func in steps.items():
            print(f"{datetime.now()} provision.py: ({self.module.title()}) {step}")

            result = eval(func)
            yield result

            if not result['success']:
                self.test_passed = False
                yield self.end_test()
                break