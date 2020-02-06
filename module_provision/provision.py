"""
    file:    provision.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Handles device provisioning and setup with the ThingPilot backend
"""

# Standard library imports
import datetime, functools, time
from subprocess import check_output

# 3rd-party library imports
import serial, socketio


sio = socketio.Client()


class ThingpilotProvisioner():
    EARHART = 'earhart'
    WRIGHT = 'wright'

    CTRL = 'AT+CTRL'
    ACK = 'OK'
    PROV_INIT = 'PROV'
    PROV_END = 'AT+END'

    def __init__(self):
        self.module = None
        self.url = None
        self.uid = None

        self.uart = None
        self.timeout_flag = False
        self.prov_passed = True
        self.total_prov_start_time = None

    def _reset_prov_passed_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.prov_passed = True

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

    def start_provision(self):
        self.total_prov_start_time = self._get_millis()
        return { 'success': True, 'message': '' }

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
            print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) received: {s}")

            if ThingpilotProvisioner.CTRL in s:
                self.uart.write(bytes(ThingpilotProvisioner.PROV_INIT, 'utf-8'))
                self.uart.write(bytes(ThingpilotProvisioner.ACK, 'utf-8'))
                print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.PROV_INIT}")
                print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.ACK}")
                break

            if self._get_millis() > (start_time + 1000):
                self.timeout_flag = True
                break
        
        if self.timeout_flag:
            return { 'success': False, 'message': 'Failed to place module into provisioning mode'}
                    
        return { 'success': True, 'message': 'Module successfully placed into provisioning mode'}

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def provision_device(self):
        start_time = self._get_millis()

        """
        while True:
            s = str(self.uart.readline())
            print(f"{datetime.now()} provision.py: ({self.module.title()}) received: {s}")

            if ThingpilotProvisioner.CTRL in s:
                self.uart.write(bytes(ThingpilotProvisioner.PROV_INIT, 'utf-8'))
                self.uart.write(bytes(ThingpilotProvisioner.ACK, 'utf-8'))
                print(f"{datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.PROV_INIT}")
                print(f"{datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.ACK}")
                break

            if self._get_millis() > (start_time + 1000):
                self.timeout_flag = True
                break
        
        """
        if self.timeout_flag:
            return { 'success': False, 'message': 'Failed to place module into provisioning mode'}
                    
        return { 'success': True, 'message': 'Did some actual provisioning, I swear'}

    @_flush_uart_input_buffer
    @_reset_timeout_flag
    def end_provision(self):
        start_time = self._get_millis()

        while True:
            self.uart.write(bytes(ThingpilotProvisioner.PROV_END, 'utf-8'))
            print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) sent: {ThingpilotProvisioner.PROV_END}")

            s = str(self.uart.readline())
            print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) received: {s}")

            if ThingpilotProvisioner.ACK in s:
                break

            if self._get_millis() > (start_time + 1000):
                break
        
        if self.uart.is_open:
            self.uart.close()

        if self.prov_passed:
            result_string = 'success <i class="fas fa-check-circle"></i>'
        else:
            result_string = 'failed <i class="fas fa-times-circle"></i>'

        total_prov_time_taken = self._get_millis() - self.total_prov_start_time

        return { 'success': self.prov_passed, 'message': f'*** Provisioning {result_string} Took: {total_prov_time_taken}ms ***' }

    @_reset_prov_passed_flag
    def provision(self):
        steps = { 
            'start_provision': 'self.start_provision()',
            'initialise_device': 'self.initialise_device()',
            'provision_device': 'self.provision_device()',
            'end_provision': 'self.end_provision()'
        }

        for step, func in steps.items():
            print(f"{datetime.datetime.now()} provision.py: ({self.module.title()}) {step}")

            result = eval(func)
            yield result

            if not result['success']:
                self.test_passed = False
                yield self.end_provision()
                break


class ProvisionerNamespace(socketio.ClientNamespace):
    def __init__(self, provisioner, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sio_connected = False

        self._provisioner = provisioner

    def on_connect(self):
        self.sio_connected = True

    def on_disconnect(self):
        self.sio_connected = False

    def on_run_provision(self, module, url, uid):
        self._provisioner.module = module
        self._provisioner.url = url
        self._provisioner.uid = uid

        for result in self._provisioner.provision():
            sio.emit('run_provision_progress', result, namespace='/DeviceNamespace')
            sio.sleep(0.2)

        
def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


def connect(n_attempts=100):
    ns = ProvisionerNamespace(ThingpilotProvisioner(), '/ProvisionerNamespace')
    sio.register_namespace(ns)

    for i in range(n_attempts):
        print(f"{datetime.datetime.now()} provision.py: Attempt {i + 1} connecting to {get_ip_address()}:80")

        try:
            sio.connect(f'http://{get_ip_address()}:80')       

            print(f"{datetime.datetime.now()} provision.py: Connected to {get_ip_address()}:80")

            break
        except socketio.exceptions.ConnectionError:
            sio.sleep(0.5)

    if ns.sio_connected:
        sio.sleep(10)

    sio.sleep(1)

    return ns.sio_connected


if __name__ == '__main__':
    if connect():
        while True:
            sio.sleep(1)
    else:
        print(f"{datetime.datetime.now()} provision.py: Failed to connect to {get_ip_address()}:80")