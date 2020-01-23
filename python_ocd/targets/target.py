"""
    file:    target.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Parent class from which all targets should be derived. A target is a Python class
             that contains device specific (i.e. STM32L0) functionality, whereas the OCDTarget
             functionality is generic, i.e. halt or reset. 
"""

# Append parent directory to path so that we can import from there
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

# Import the OCD interface from python_ocd.py
from python_ocd import OCD


class OCDTarget(OCD):
    def __init__(self, tcl_ip='localhost', tcl_port=6666):
        super().__init__(tcl_ip, tcl_port)
        
        

    


if __name__ == '__main__':
    myTarget = OCDTarget()
