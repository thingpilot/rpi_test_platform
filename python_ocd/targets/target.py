"""
    file:    target.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Parent class from which all targets should be derived. A target is a Python class
             that contains device specific (i.e. STM32L0) functionality, whereas the OCDTarget
             functionality is generic, i.e. halt or reset. 
"""

# Standard library imports
import inspect, os, re, sys

# Append parent directory to path so that we can import from there
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

# Import the OCD interface from python_ocd.py
from python_ocd import OCD


class OCDTarget(OCD):
    STATES = [ 'unknown', 'halted', 'running', 'reset', 'debug-running' ]

    def __init__(self, tcl_ip='localhost', tcl_port=6666):
        super().__init__(tcl_ip, tcl_port)

    def get_state(self):
        targets = self.send('targets')
        state = ''

        for state in OCDTarget.STATES:
            if state in targets['message']:
                return state

        return False

    def init(self):
        return self.send('init')

    def reset_run(self, verify=True):
        result = self.send('reset run')
        
        if verify:
            return self.get_state() == 'running'
        else:
            return result

    def reset_halt(self, verify=True):
        result = self.send('reset halt')
        
        if verify:
            return self.get_state() == 'halted'
        else:
            return result

    def targets(self):
        return self.send('targets')

    def flash_write_image_bin(self, firmware, address):
        result = self.send(f'flash write_image erase {firmware} {address}')

        bytes_wrote_re = re.search('(wrote\s\d{3,}\sbytes)', result['message'])

        if bytes_wrote_re:
            result['bytes_wrote'] = bytes_wrote_re.group().split()[1]
            result['success'] = True
        else:
            result['success'] = False

        return result

    def verify_image(self, firmware, address):
        result = self.send(f'verify_image {firmware} {address}')

        if 'verified' in result['message'].lower():
            result['success'] = True
        else:
            result['success'] = False

        return result

    def program_bin(self, firmware, address, verify=True):
        if not self.init():
            return { 'success': False, 'message': 'Failed to init target' }

        if not self.reset_halt():
            return { 'success': False, 'message': 'Failed to reset halt target' }

        program_result = self.flash_write_image_bin(firmware, address)
        if not program_result['success']:
            return { 'success': False, 'message': 'Failed writing to flash memory' }

        verify_result = self.verify_image(firmware, address)
        if not verify_result['success']:
            return { 'success': False, 'message': 'Failed to verify flash memory' }

        return { 'success': True, 'message': 'Successfully programmed target' }
        