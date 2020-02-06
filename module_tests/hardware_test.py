"""
    file:    hardware_test.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python script to verify Wright/Earhart module hardware functionality. This will test
             that all available GPIO pins function correctly as well as all available comms busses,
             including I2C, SPI and UART.
"""

# Standard library imports
import datetime, functools, time
from subprocess import check_output

# 3rd-party library imports
import RPi.GPIO as gpio
import serial, socketio

# Thingpilot library imports
if __name__ == '__main__':
    import pinmap
else:
    from module_tests import pinmap


sio = socketio.Client()


class TestCommands():
    CTRL = 'AT+CTRL'
    TEST_INIT = 'TEST'
    TEST_END  = 'AT+END'
    ACK       = 'OK'
    TEST_GPIO = 'AT+GPIO='


class HardwareTest():
    EARHART = 'earhart'
    WRIGHT = 'wright'

    def __init__(self):
        self.module = None
        self.pinmap = None
        self.uart = None
        self.timeout_flag = False
        self.test_passed = True
        self.total_test_start_time = None

    def _reset_test_passed_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.test_passed = True

            return func(self, *args, **kwargs)

        return wrap

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

    def set_module(self, module):
        self.module = module

        if self.module == HardwareTest.EARHART:
            self.pinmap = pinmap.earhart
        elif self.module == HardwareTest.WRIGHT:
            self.pinmap = pinmap.wright
        else:
            self.pinmap = None

    def start_test(self, module):
        self.set_module(module)
        self.total_test_start_time = self._get_millis()

        return { 'success': True, 'message': '' }

    def verify_pinmap(self):
        print('VERIFY PINMAP')
        if self.pinmap is None:
            return { 'success': False, 'message': 'Unknown module selected'}

        return { 'success': True, 'message': f'Successfully loaded pin mapping for {self.module.title()}'}

    @_reset_timeout_flag
    def initialise_device(self):
        try:
            self.uart = serial.Serial('/dev/serial0', 9600, timeout=0.2)
        except serial.serialutil.SerialException:
            return { 'success': False, 'message': 'Failed to connect to port /dev/serial0'}

        if not self.uart.is_open:
            self.uart.open()

        if not self.uart.is_open:
            return { 'success': False, 'message': 'Failed to open port /dev/serial0'}

        start_time = self._get_millis()

        while True:
            s = str(self.uart.readline())
            print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) received: {s}")

            if TestCommands.CTRL in s:
                self.uart.write(bytes(TestCommands.TEST_INIT, 'utf-8'))
                self.uart.write(bytes(TestCommands.ACK, 'utf-8'))
                print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) sent: {TestCommands.ACK}")
                break

            if self._get_millis() > (start_time + 1000):
                self.timeout_flag = True
                break
        
        if self.timeout_flag:
            return { 'success': False, 'message': 'Failed to place DUT into test mode'}
                    
        return { 'success': True, 'message': 'DUT successfully placed into test mode'}

    def start_test_gpio(self):
        return { 'success': True, 'message': 'Starting GPIO test'}

    def _toggle_test_gpio(self, cpu_pin, rpi_pin, expected_pin_state):
        gpio.setmode(gpio.BCM)
        gpio.setup(rpi_pin, gpio.IN)
        test_passed = False

        self.uart.write(bytes(f'{TestCommands.TEST_GPIO}{cpu_pin},{expected_pin_state}', 'utf-8'))
        print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) sent: {TestCommands.TEST_GPIO}{cpu_pin},{expected_pin_state}")
        start_time = self._get_millis()

        while True: 
            result = str(self.uart.readline())
            print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) received: {result}")

            if f'GPIO: {cpu_pin}, {expected_pin_state}' in result:
                actual_pin_state = gpio.input(rpi_pin)

                if actual_pin_state == expected_pin_state:
                    self.uart.write(bytes(TestCommands.ACK, 'utf-8'))
                    print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) sent: {TestCommands.ACK}")
                    test_passed = True
                    break
            
            if self._get_millis() > (start_time + 1000):
                test_passed = False
                break

        gpio.cleanup()

        return test_passed

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def test_gpio(self):
        test_start_time = self._get_millis()
        test_results = { 'time_taken': 0, 'type': 'GPIO', 'results': [] }
        test_passed = True

        for pin, mapping in self.pinmap.items():
            if mapping['bus'] == 'SWD' or mapping['bus'] == 'PWR' or mapping['bus'] == 'RSVD' or mapping['bus'] == 'UART':
                continue

            rpi_pin = mapping['rpi_pin_no']
            cpu_pin = mapping['cpu_pin_no']

            HIGH_RESULT = self._toggle_test_gpio(cpu_pin, rpi_pin, 1)
            LOW_RESULT = self._toggle_test_gpio(cpu_pin, rpi_pin, 0)  

            if not HIGH_RESULT or not LOW_RESULT: 
                test_passed = False   

            test_results['results'].append({ 'pin': pin, 'high': HIGH_RESULT, 'low': LOW_RESULT })  

        time_taken = self._get_millis() - test_start_time
        test_results['time_taken'] = time_taken

        return { 'success': test_passed, 'message': 'GPIO', 'results': test_results }


    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def end_test(self):
        start_time = self._get_millis()

        while True:
            self.uart.write(bytes(TestCommands.TEST_END, 'utf-8'))
            print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) sent: {TestCommands.TEST_END}")

            s = str(self.uart.readline())
            print(f"{datetime.datetime.now()} hardware_test.py: ({self.module.title()}) received: {s}")

            if TestCommands.ACK in s:
                break

            if self._get_millis() > (start_time + 1000):
                break

        if self.uart.is_open:
            self.uart.close()

        if self.test_passed:
            result_string = 'success <i class="fas fa-check-circle"></i>'
        else:
            result_string = 'failed <i class="fas fa-times-circle"></i>'

        total_test_time_taken = self._get_millis() - self.total_test_start_time

        return { 'success': True, 'message': f'*** Hardware test {result_string} Took: {total_test_time_taken}ms ***' }

    @_reset_test_passed_flag
    def run_test(self, module):
        steps = { 
            'start_test': 'self.start_test(module)',
            'verify_pinmap': 'self.verify_pinmap()',
            'initialise_device': 'self.initialise_device()',
            'start_test_gpio': 'self.start_test_gpio()',
            'test_gpio': 'self.test_gpio()',
            'end_test': 'self.end_test()'
        }

        for step, func in steps.items():
            print(f"{datetime.datetime.now()} hardware_test.py: ({module.title()}) {step}")

            result = eval(func)
            yield result

            if not result['success']:
                self.test_passed = False
                yield self.end_test()
                break


class HWTestNamespace(socketio.ClientNamespace):
    def __init__(self, hw_test, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sio_connected = False

        self._hw_test = hw_test

    def on_connect(self):
        self.sio_connected = True

    def on_disconnect(self):
        self.sio_connected = False

    def on_run_test(self, module):
        for result in self._hw_test.run_test(module):
            sio.emit('run_test_progress', result, namespace='/DeviceNamespace')
            sio.sleep(0.2)


def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


def connect(n_attempts=100):
    ns = HWTestNamespace(HardwareTest(), '/HWTestNamespace')
    sio.register_namespace(ns)

    for i in range(n_attempts):
        print(f"{datetime.datetime.now()} hardware_test.py: Attempt {i + 1} connecting to {get_ip_address()}:80")

        try:
            sio.connect(f'http://{get_ip_address()}:80')       

            print(f"{datetime.datetime.now()} hardware_test.py: Connected to {get_ip_address()}:80")

            break
        except socketio.exceptions.ConnectionError:
            sio.sleep(0.1)

    if ns.sio_connected:
        sio.sleep(10)

    sio.sleep(1)

    return ns.sio_connected


if __name__ == '__main__':
    if connect():
        while True:
            sio.sleep(1)
    else:
        print(f"{datetime.datetime.now()} hardware_test.py: Failed to connect to {get_ip_address()}:80")