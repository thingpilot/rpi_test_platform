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
        self.test_passed = True
        self.total_test_start_time = self._get_millis()

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

    def start_test(self):
        date_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
        return { 'success': True, 'message': f'*** Beginning {self.module.title()} hardware test at: {date_time} ***\n' }

    def verify_pinmap(self):
        if self.pinmap is None:
            return { 'success': False, 'message': '    HW Test (init) - Unknown module selected\n'}

        return { 'success': True, 'message': f'    HW Test (init) - Successfully loaded pin mapping for {self.module.title()}\n'}

    @_reset_timeout_flag
    def initialise_device(self):
        try:
            self.uart = serial.Serial('/dev/serial0', 9600, timeout=0.2)
        except serial.serialutil.SerialException:
            return { 'success': False, 'message': '    HW Test (init) - Failed to connect to port /dev/serial0\n'}

        if not self.uart.is_open:
            self.uart.open()

        if not self.uart.is_open:
            return { 'success': False, 'message': '    HW Test (init) - Failed to open port /dev/serial0\n'}

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
            return { 'success': False, 'message': '    HW Test (init) - Failed to place DUT into test mode\n'}
                    
        return { 'success': True, 'message': '    HW Test (init) - DUT successfully placed into test mode\n'}

    def start_test_gpio(self):
        return { 'success': True, 'message': '    HW Test (GPIO) - Starting GPIO test\n'}

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def test_gpio(self):
        test_start_time = self._get_millis()
        test_results = { 'time_taken': 0, 'type': 'GPIO', 'results': [] }
        test_passed = True

        gpio.setmode(gpio.BCM)

        for pin, mapping in self.pinmap.items():
            if mapping['bus'] == 'SWD' or mapping['bus'] == 'PWR' or mapping['bus'] == 'RSVD' or mapping['bus'] == 'UART':
                continue

            HIGH_RESULT = False
            LOW_RESULT = False

            rpi_pin_no = mapping['rpi_pin_no']
            cpu_pin_no = mapping['cpu_pin_no']

            gpio.setup(rpi_pin_no, gpio.IN)

            self.uart.write(bytes(f'{TestCommands.TEST_GPIO}{cpu_pin_no},1', 'utf-8'))
            start_time = self._get_millis()

            while True: 
                result = str(self.uart.readline())

                if f'GPIO: {cpu_pin_no}, 1' in result:
                    pin_state = gpio.input(rpi_pin_no)

                    if pin_state == 1:
                        self.uart.write(bytes(TestCommands.ACK, 'utf-8'))
                        HIGH_RESULT = True
                        break
                
                if self._get_millis() > (start_time + 1000):
                    test_passed = False
                    break

            self.uart.write(bytes(f'{TestCommands.TEST_GPIO}{cpu_pin_no},0', 'utf-8'))
            start_time = self._get_millis()

            while True: 
                s = str(self.uart.readline())

                if f'GPIO: {cpu_pin_no}, 0' in s:
                    pin_state = gpio.input(rpi_pin_no)
                    
                    if pin_state == 0:
                        self.uart.write(bytes(TestCommands.ACK, 'utf-8'))
                        LOW_RESULT = True
                        break
                
                if self._get_millis() > (start_time + 1000):
                    test_passed = False
                    break

            test_results['results'].append({ 'pin': pin, 'high': HIGH_RESULT, 'low': LOW_RESULT })

        gpio.cleanup()

        time_taken = self._get_millis() - test_start_time
        test_results['time_taken'] = time_taken

        return { 'success': test_passed, 'message': 'GPIO', 'results': test_results }

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

        if self.test_passed:
            result_string = 'PASSED'
        else:
            result_string = 'FAILED'

        total_test_time_taken = self._get_millis() - self.total_test_start_time

        return { 'success': True, 'message': f'*** Ended {self.module.title()} hardware test. Took: {total_test_time_taken}ms ***\n    HW Test - {result_string}\n' }

    def run_test(self):
        steps = { 
            'start_test': 'self.start_test()',
            'verify_pinmap': 'self.verify_pinmap()',
            'initialise_device': 'self.initialise_device()',
            'start_test_gpio': 'self.start_test_gpio()',
            'test_gpio': 'self.test_gpio()',
            'end_test': 'self.end_test()'
        }

        for step, func in steps.items():
            print(step)
            result = eval(func)
            yield result

            if not result['success']:
                self.test_passed = False
                yield self.end_test()
                break