"""
    file:    stm32l0.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Target class for STM32L0 processors. Implements target-specific methods, such as 
             extraction of the STM32 unique ID.
"""

if __name__ == '__main__':
    # Import Parent target class
    from target.target import OCDTarget
else:
    from python_ocd.targets.target import OCDTarget


class STM32L0(OCDTarget):
    PGM_START_ADDRESS = '0x08000000'

    def __init__(self, openocd_cfg='stm32l0_ocd.cfg', tcl_ip='localhost', tcl_port=6666):
        super().__init__(openocd_cfg, tcl_ip, tcl_port)

    def get_unique_id(self):
        result = self.send('mdw 0x1FF80050 3')

        if result['success']:
            result['message'] = result['message'][12:38]
        
        return result
            