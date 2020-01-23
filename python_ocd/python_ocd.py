"""
    file:    python_ocd.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python Tcl client for OpenOCD. Allows the sending of commands to a 
             microprocessor via OpenOCD and monitors the return status. 
"""

# Standard library imports
import functools, signal, socket


class TimeoutError(Exception): 
    pass


class OCD():
    COMMAND_TOKEN = '\x1a'

    def __init__(self, tcl_ip='localhost', tcl_port=6666):
        self.tcl_ip = tcl_ip
        self.tcl_port = tcl_port
        self.buffer_size = 4096
        self.timeout_flag = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.sock.connect((self.tcl_ip, self.tcl_port))
        return self

    def __exit__(self, type, value, traceback):
        self.sock.close()

    def _reset_timeout_flag(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            self.timeout_flag = False

            return func(self, *args, **kwargs)

        return wrap

    def _handle_timeout(self, signum, frame):
        self.timeout_flag = True
        raise TimeoutError

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

    @_reset_timeout_flag
    def send(self, command, recv_string=None, timeout_s=10):
        success = False
        recv_data = None

        data = (command + OCD.COMMAND_TOKEN).encode('utf-8')

        self.sock.send(data)

        if timeout_s:
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(timeout_s)
            
            try:
                recv_data = self._recv()
            except TimeoutError: 
                pass
            finally:
                signal.alarm(0)

        if not self.timeout_flag:
            if recv_string is not None:
                if recv_string in recv_data:
                    success = True
                else:
                    success = False
            else:
                success = True
        else:
            success = False

        return { 'success': success, 'message': recv_data }


if __name__ == '__main__':
    with OCD() as openocd:
        response = openocd.send('init')
        print(response)
        response = openocd.send('reset')
        print(response)
        response = openocd.send('halt')
        print(response)

        response = openocd.send('flash write_image erase firmware/blink-fast.bin 0x08000000')
        print(response)
        
        response = openocd.send('verify_image firmware/blink-fast.bin 0x08000000', recv_string='verified')
        print(response)