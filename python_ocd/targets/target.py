"""
    file:    target.py
    version: 0.2.0
    author:  Adam Mitchell
    brief:   Parent class from which all targets should be derived. A target is a Python class
             that contains device specific (i.e. STM32L0) functionality, whereas the OCDTarget
             functionality is generic, i.e. halt or reset. 
"""

# Standard library imports
import inspect, os, re, sys


if __name__ == '__main__':
    # Append parent directory to path so that we can import from there
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir) 

    # Import the OCD interface from python_ocd.py
    from python_ocd import OCD
else:
    try:
        from python_ocd.python_ocd import OCD
    except ModuleNotFoundError:
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        sys.path.insert(0, parentdir) 

        # Import the OCD interface from python_ocd.py
        from python_ocd import OCD

import eventlet; eventlet.monkey_patch()


class OCDTarget(OCD):
    STATES = [ 'unknown', 'halted', 'running', 'reset', 'debug-running' ]

    def __init__(self, openocd_cfg, tcl_ip='localhost', tcl_port=6666):
        super().__init__(openocd_cfg, tcl_ip, tcl_port)

    def get_state(self):
        result = self.send('targets')
        state = ''

        if result['success']:
            for state in OCDTarget.STATES:
                if state in result['message']:
                    result['state'] = state
                    result['success'] = True
                    break
            
            if not result['success']:
                result['success'] = False
        else:
            result['success'] = False

        return result

    def init(self):
        result = self.send('init')

        if result['success']:
            result['message'] = 'Target CPU successfully initialised'
        else:
            result['message'] = 'Failed to initialise target CPU'

        return result

    def reset_run(self, verify=True):
        result = self.send('reset run')

        state = self.get_state()
        if state['success']:   
            if verify:
                if self.get_state()['state'] == 'running':
                    result['success'] = True
                    result['message'] = 'Target CPU running'
                else:
                    result['success'] = False
                    result['message'] = 'Failed to make target CPU run'
        
        return result

    def reset_halt(self, verify=True):
        result = self.send('reset halt')
        
        state = self.get_state()
        if state['success']:   
            if verify:
                if self.get_state()['state'] == 'halted':
                    result['success'] = True
                    result['message'] = 'Target CPU successfully halted'
                else:
                    result['success'] = False
                    result['message'] = 'Failed to halt target CPU'
        
        return result

    def targets(self):
        return self.send('targets')

    def flash_write_image_bin(self, firmware, address):
        result = self.send(f'flash write_image erase {firmware} {address}')

        if result['success']:
            bytes_wrote_re = re.search('(wrote\s\d{3,}\sbytes)', result['message'])

            if bytes_wrote_re:
                result['bytes_wrote'] = bytes_wrote_re.group().split()[1]
                result['success'] = True
            else:
                result['success'] = False

        return result

    def verify_image(self, firmware, address):
        result = self.send(f'verify_image {firmware} {address}')

        if result['success']:
            if 'verified' in result['message'].lower():
                result['success'] = True
            else:
                result['success'] = False

        return result

    def program_bin(self, firmware, address, verify=True):
        if __name__ == '__main__':
            firmware = f'../firmware/{firmware}'
        else:
            firmware = f'python_ocd/firmware/{firmware}'

        func_dict = { 'init': 'self.init()',
                      'reset halt': 'self.reset_halt()',
                      'flash write_image erase': f'self.flash_write_image_bin("{firmware}", "{address}")',
                      'verify_image': f'self.verify_image("{firmware}", "{address}")',
                      'init': 'self.init()',
                      'reset run': 'self.reset_run()'
                    }

        for name, func in func_dict.items():
            result = eval(func)

            if not result['success']:
                result['message'] = f'{result["message"]}: {name}'
                yield result

                break
            else:
                yield result
        