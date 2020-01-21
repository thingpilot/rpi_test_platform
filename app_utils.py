"""
    file:    app_utils.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Utility functions for Flask
"""

# Standard library imports
from subprocess import check_output


def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip