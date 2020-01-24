"""
    file:    stm32l0.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Target class for STM32L0 processors. Implements target-specific methods, such as 
             extraction of the STM32 unique ID.
"""

# Import Parent target class
from target import OCDTarget


class STM32L0(OCDTarget):
    def __init__(self, tcl_ip='localhost', tcl_port=6666):
        super().__init__(tcl_ip, tcl_port)


if __name__ == '__main__':
    with STM32L0() as cpu:
        print(cpu.program_bin('firmware/blink-fast.bin', '0x08000000'))