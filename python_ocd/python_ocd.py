"""
    file:    python_ocd.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python Tcl client for OpenOCD. Allows the sending of commands to a 
             microprocessor via OpenOCD and monitors the return status. 
"""

# Standard library imports
import functools
import os
import subprocess
import sys
import time

try:
    import thread
except ImportError:
    import _thread as thread

# Import eventlet compatible socket and threading libraries
import eventlet
socket = eventlet.import_patched('socket')
threading = eventlet.import_patched('threading')


class TimeoutError(Exception): 
    pass


class OCD():
    COMMAND_TOKEN = '\x1a'
    INIT_DELAY    = 0.1

    def __init__(self, openocd_cfg, tcl_ip='localhost', tcl_port=6666):
        self.openocd_cfg = f'../configs/{openocd_cfg}'
        self.tcl_ip = tcl_ip
        self.tcl_port = tcl_port
        self.buffer_size = 4096
        self.timeout_flag = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _reset_timeout_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.timeout_flag = False

            return func(self, *args, **kwargs)

        return wrap

    def _handle_timeout(self, signum, frame):
        self.timeout_flag = True
        raise TimeoutError

    def _deinit_openocd(self):
        os.system('sudo pkill -9 openocd')

    @_reset_timeout_flag
    def _init_openocd(self, timeout_s=5):
        try:
            process = subprocess.Popen(['sudo', 'openocd', '-f', f'{self.openocd_cfg}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self._deinit_openocd()
            return False

        signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(timeout_s)

        try:
            for line in process.stderr:
                line_decoded = line.decode('utf-8')
                
                if '6666 for tcl connections' in line_decoded.lower():
                    time.sleep(OCD.INIT_DELAY)
                    break
        except TimeoutError:
            pass
        finally:
            signal.alarm(0)

        if self.timeout_flag:
            return False
        else:
            return True

    def __enter__(self):
        if self._init_openocd():
            self.sock.connect((self.tcl_ip, self.tcl_port))
        
        return self

    def __exit__(self, type, value, traceback):
        self.sock.close()
        self._deinit_openocd()

    def _recv(self):
        data = bytes()

        while True:
            chunk = self.sock.recv(self.buffer_size)
            data += chunk
            if bytes(OCD.COMMAND_TOKEN, encoding='utf-8') in chunk:
                break

        data = data.decode('utf-8').strip()
        data = data[:-1]

        return data

    def connect(self):
        self.__enter__()

    def disconnect(self):
        self.__exit__(*sys.exc_info())

    def get_buffer_size(self):
        return self.buffer_size

    def set_buffer_size(self, buffer_size_bytes):
        self.buffer_size(buffer_size_bytes)

        return self.get_buffer_size()

    @_reset_timeout_flag
    def send(self, command, recv_string=None, timeout_s=10):
        success = False
        recv_data = None
        error = ''

        data = (command + OCD.COMMAND_TOKEN).encode('utf-8')

        try:
            self.sock.send(data)
        except BrokenPipeError as e:
            return { 'success': False, 'message': 'Failed to send to Tcl server. Server appears to be down', 'error': e}

        if timeout_s:
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(timeout_s)
            
            try:
                recv_data = self._recv()
            except TimeoutError: 
                pass
            finally:
                signal.alarm(0)
        else:
            recv_data = self._recv()

        if not self.timeout_flag:
            if recv_string is not None:
                if recv_string in recv_data:
                    success = True
                else:
                    success = False
                    error = f'{recv_string} not in {recv_data}'
            else:
                success = True
        else:
            success = False
            error = 'Timed out'

        return { 'success': success, 'message': recv_data, 'error': error }