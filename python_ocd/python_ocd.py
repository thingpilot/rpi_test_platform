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
import socket
import subprocess
import sys
import threading

try:
    import thread
except ImportError:
    import _thread as thread

# Monkey patch standard libs for eventlet compatibility
import eventlet; eventlet.monkey_patch()


class TimeoutError(Exception): 
    pass


class OCD():
    COMMAND_TOKEN = '\x1a'

    def __init__(self, openocd_cfg, tcl_ip='localhost', tcl_port=6666):
        if __name__ == '__main__':
            self.openocd_cfg = f'../configs/{openocd_cfg}'
        else:
            self.openocd_cfg = f'python_ocd/configs/{openocd_cfg}'
            
        self.tcl_ip = tcl_ip
        self.tcl_port = tcl_port
        self.buffer_size = 4096
        self.timeout_flag = False
        self._ocd_process = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _reset_timeout_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.timeout_flag = False

            return func(self, *args, **kwargs)

        return wrap

    def _handle_timeout(self):
        self.timeout_flag = True
        raise TimeoutError

    def _deinit_openocd(self):
        if self._ocd_process is None:
            os.system('sudo pkill -9 openocd')
        else:
            self._ocd_process.kill()

    @_reset_timeout_flag
    def _init_openocd(self, timeout_s=5):
        try:
            self._ocd_process = subprocess.Popen(
                ['sudo', 'openocd', '-f', f'{self.openocd_cfg}'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError:
            self._ocd_process = None
            self._deinit_openocd()
            return False

        timer = threading.Timer(timeout_s, self._handle_timeout)
        timer.start()

        try:
            for line in self._ocd_process.stderr:
                line_decoded = line.decode('utf-8')
                
                if '6666 for tcl connections' in line_decoded.lower():
                    break
        except TimeoutError:
            pass
        finally:
            timer.cancel()

        if self.timeout_flag:
            return False
        else:
            return True

    def __enter__(self):
        if self._init_openocd():
            try:
                self.sock.connect((self.tcl_ip, self.tcl_port))
            except ConnectionError:
                return False
        
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
    def send(self, command, recv_string=None, timeout_s=20):
        success = False
        recv_data = None
        error = ''

        data = (command + OCD.COMMAND_TOKEN).encode('utf-8')

        try:
            self.sock.send(data)
        except BrokenPipeError as e:
            return { 'success': False, 'message': 'Failed to send to Tcl server. Server appears to be down', 'error': e}

        if timeout_s:
            timer = threading.Timer(timeout_s, self._handle_timeout)
            timer.start()
            
            try:
                try:
                    recv_data = self._recv()
                except ConnectionResetError as e:
                    timer.cancel()
                    return { 'success': False, 'message': 'Module likely isn\'t connected properly to the test HAT', 'error': e }
            except TimeoutError: 
                pass
            finally:
                timer.cancel()
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