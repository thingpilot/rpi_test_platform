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

# 3rd-party library imports
import RPi.GPIO as gpio
import serial

# Thingpilot library imports
if __name__ == '__main__':
    import pinmap
else:
    from module_tests import pinmap


class TimeoutError(Exception): 
    pass


class TestCommands():
    TEST_INIT = 'AT+MODTEST'
    TEST_END  = 'AT+ENDTEST'
    ACK       = 'OK'
    TEST_GPIO = 'AT+GPIO='


class HardwareTest():
    EARHART = 'earhart'
    WRIGHT = 'wright'

    def __init__(self, module):
        self.module = module

        if self.module == HardwareTest.EARHART:
            self.pinmap = pinmap.earhart
        elif self.module == HardwareTest.WRIGHT:
            self.pinmap = pinmap.wright
        else:
            self.pinmap = None

        self.uart = None
        self.timeout_flag = False

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

    def verify_pinmap(self):
        if self.pinmap is None:
            return { 'success': False, 'message': 'Unknown module selected\n'}

        return { 'success': True, 'message': f'Successfully loaded pin mapping for {self.module}\n'}

    @_reset_timeout_flag
    def initialise_device(self):
        try:
            self.uart = serial.Serial('/dev/serial0', 9600, timeout=0.2)
        except serial.serialutil.SerialException:
            return { 'success': False, 'message': 'Failed to connect to port /dev/serial0\n'}

        if not self.uart.is_open:
            self.uart.open()

        if not self.uart.is_open:
            return { 'success': False, 'message': 'Failed to open port /dev/serial0\n'}

        start_time = self._get_millis()

        while True:
            s = str(self.uart.readline())
            print(s)

            if TestCommands.TEST_INIT in s:
                self.uart.write(bytes(TestCommands.ACK, 'utf-8'))
                break

            if self._get_millis() > (start_time + 1000):
                self.timeout_flag = True
                break
        
        if self.timeout_flag:
            return { 'success': False, 'message': 'Failed to place DUT into test mode\n'}
                    
        return { 'success': True, 'message': 'DUT successfully placed into test mode\n'}

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def test_gpio(self):
        start_time = self._get_millis()

        for pin, mapping in self.pinmap.items():
            while True: 
                self.uart.write(bytes(f'{TestCommands.TEST_GPIO}1,1', 'utf-8'))

                s = str(self.uart.readline())
                print(s)

                if 'GPIO: 1, 1' in s:
                    print(f"Received: {s}")
                    break

                if self._get_millis() > (start_time + 1000):
                    break

        return { 'success': True, 'message': 'Some GPIO stuff\n' }

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def end_test(self):
        start_time = self._get_millis()

        while True:
            self.uart.write(bytes(TestCommands.TEST_END, 'utf-8'))

            s = str(self.uart.readline())
            print(s)

            if 'TEST COMPLETE' in s:
                print(f"Received: {s}")
                break

            if self._get_millis() > (start_time + 1000):
                break

        if self.uart.is_open:
            self.uart.close()

        return { 'success': True, 'message': f'Test complete\n' }

    def run_test(self):
        steps = { 'verify_pinmap': 'self.verify_pinmap()',
                  'initialise_device': 'self.initialise_device()',
                  'test_gpio': 'self.test_gpio()',
                  'end_test': 'self.end_test()'
        }

        for step, func in steps.items():
            print(step)
            result = eval(func)
            yield result

            if not result['success']:
                break