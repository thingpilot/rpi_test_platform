"""
    file:    hardware_test.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python script to verify Wright/Earhart module hardware functionality. This will test
             that all available GPIO pins function correctly as well as all available comms busses,
             including I2C, SPI and UART.
"""

from module_tests import pinmap

class HardwareTest():
    EARHART = 'earhart'
    WRIGHT = 'wright'

    def __init__(self, module):
        self.module = module

        if self.module == HardwareTest.EARHART:
            self.pinmap = pinmap.earhart
        elif self.module == HardwareTest.WRIGHT:
            self.pinmap = pinmap.wright
        else:
            self.pinmap = None