"""
    file:    stm32l0.py
    version: 0.2.0
    author:  Adam Mitchell
    brief:   Target class for STM32L0 processors. Implements target-specific methods, such as 
             extraction of the STM32 unique ID.
"""

import datetime, functools, inspect
from subprocess import check_output

if __name__ == '__main__':
    # Import Parent target class
    from target import OCDTarget
else:
    from python_ocd.targets.target import OCDTarget

import socketio


sio = socketio.Client()


class MutexLockedError(Exception):
    def __init__(self, func):
        success = False
        message = 'Operation currently in progress'
        error   = f'MutexLockedError: {func}'

        result = { 'success': success, 'message': message, 'error': error }
        
        sio.emit(
            func.split('on_')[1] + '_progress', 
            result, 
            namespace='/DeviceNamespace'
        )


class CPUCommsError(Exception):
    def __init__(self, func):
        success = False
        message = 'Failed to connect to Tcl server'
        error   = f'CPUCommsError: {func}'

        result = { 'success': success, 'message': message, 'error': error }

        sio.emit(
            func.split('on_')[1] + '_progress', 
            result, 
            namespace='/DeviceNamespace'
        )


class SIONotConnectedError(Exception):
    def __init__(self, func):
        success = False
        message = 'Failed to connect to Tcl server'
        error   = f'CPUCommsError: {func}'

        result = { 'success': success, 'message': message, 'error': error }

        print(result)


class STM32L0(OCDTarget):
    PGM_START_ADDRESS = '0x08000000'

    def __init__(self, openocd_cfg='stm32l0_ocd.cfg', tcl_ip='localhost', tcl_port=6666):
        super().__init__(openocd_cfg, tcl_ip, tcl_port)

    def get_unique_id(self):
        result = self.init()
        result = self.reset_halt()
        result = self.send('mdw 0x1FF80050 3')

        if result['success']:
            if '00000000 00000000 00000000' in result['message'] or result['message'] == '':
                result['success'] = False

            result['message'] = result['message'][12:38]
        
        return result


class STM32L0Namespace(socketio.ClientNamespace):
    def __init__(self, cpu, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sio_connected = False

        self._mutex_lock = False
        self._cpu = cpu

    def _mutex_use_cpu(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            res = None

            try:
                if not self._mutex_lock:
                    self._mutex_lock = True

                    if self.sio_connected:
                        with self._cpu:
                            if self._cpu:
                                res = func(self, *args, **kwargs)   
                            else:
                                self._mutex_lock = False
                                raise CPUCommsError(wrapper.__name__)
                    
                        self._mutex_lock = False
                    else:
                        self._mutex_lock = False
                        raise SIONotConnectedError(wrapper.__name__)
                else:
                    raise MutexLockedError(wrapper.__name__)
            except (MutexLockedError, SIONotConnectedError, CPUCommsError):
                pass
            
            if res is not None:
                return res

        return wrapper

    def on_connect(self):
        self.sio_connected = True

    def on_disconnect(self):
        self.sio_connected = False

    @_mutex_use_cpu
    def on_get_unique_id(self, data):
        sio.emit('get_unique_id_progress', self._cpu.get_unique_id(), namespace='/DeviceNamespace')

    @_mutex_use_cpu
    def on_program_bin(self, binary):
        for result in self._cpu.program_bin(binary, STM32L0.PGM_START_ADDRESS):
            sio.emit('program_bin_progress', result, namespace='/DeviceNamespace')

    @_mutex_use_cpu
    def on_run_test(self, data):
        sio.emit('run_test_progress', self._cpu.init(), namespace='/DeviceNamespace')
        sio.emit('run_test_progress', self._cpu.reset_run(), namespace='/DeviceNamespace')

    @_mutex_use_cpu
    def on_run_provision(self, data):
        sio.emit('run_provision_progress', self._cpu.init(), namespace='/DeviceNamespace')
        sio.emit('run_provision_progress', self._cpu.reset_run(), namespace='/DeviceNamespace')


def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


def connect(n_attempts=100):
    ns = STM32L0Namespace(STM32L0(), '/STM32L0Namespace')
    sio.register_namespace(ns)

    for i in range(n_attempts):
        print(f"{datetime.datetime.now()} stm32l0.py: Attempt {i + 1} connecting to {get_ip_address()}:80")

        try:
            sio.connect(f'http://{get_ip_address()}:80')       

            print(f"{datetime.datetime.now()} stm32l0.py: Connected to {get_ip_address()}:80")

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
        print(f"{datetime.datetime.now()} stm32l0.py: Failed to connect to {get_ip_address()}:80")


