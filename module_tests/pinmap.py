"""
    file:    pinmap.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python dictionaries listing pin mappings for each Thingpilot module 
"""


wright = { 
    1:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    2:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    3:  { 'bus': 'UART',  'signal': 'TXU',         'cpu_pin': 'PA2',   'cpu_pin_no': 2,   'rpi_pin_no': 15  },
    4:  { 'bus': 'UART',  'signal': 'RXU',         'cpu_pin': 'PA3',   'cpu_pin_no': 3,   'rpi_pin_no': 14  },
    5:  { 'bus': 'SPI',   'signal': 'NSS',         'cpu_pin': 'PA4',   'cpu_pin_no': 4,   'rpi_pin_no': 8   },
    6:  { 'bus': 'SPI',   'signal': 'SCK',         'cpu_pin': 'PA5',   'cpu_pin_no': 5,   'rpi_pin_no': 11  },
    7:  { 'bus': 'SPI',   'signal': 'MISO',        'cpu_pin': 'PA6',   'cpu_pin_no': 6,   'rpi_pin_no': 9   },
    8:  { 'bus': 'SPI',   'signal': 'MOSI',        'cpu_pin': 'PA7',   'cpu_pin_no': 7,   'rpi_pin_no': 10  },
    9:  { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    10: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    11: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    12: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    13: { 'bus': 'GPIO',  'signal': 'GPIO1',       'cpu_pin': 'PB0',   'cpu_pin_no': 16,  'rpi_pin_no': 4   },
    14: { 'bus': 'I2C',   'signal': 'SCL',         'cpu_pin': 'PA9',   'cpu_pin_no': 9,   'rpi_pin_no': 3   },
    15: { 'bus': 'I2C',   'signal': 'SDA',         'cpu_pin': 'PA10',  'cpu_pin_no': 10,  'rpi_pin_no': 2   },
    16: { 'bus': 'SWD',   'signal': 'SWDIO',       'cpu_pin': 'PA13',  'cpu_pin_no': 13,  'rpi_pin_no': 24  },
    17: { 'bus': 'SWD',   'signal': 'SWCLK',       'cpu_pin': 'PA14',  'cpu_pin_no': 14,  'rpi_pin_no': 25  },
    18: { 'bus': 'SWD',   'signal': 'NRST',        'cpu_pin': 'NRST',  'cpu_pin_no': 999, 'rpi_pin_no': 18  },
    19: { 'bus': 'GPIO',  'signal': 'GPIO2',       'cpu_pin': 'PB1',   'cpu_pin_no': 17,  'rpi_pin_no': 27  },
    20: { 'bus': 'GPIO',  'signal': 'WKUP1',       'cpu_pin': 'PA0',   'cpu_pin_no': 0,   'rpi_pin_no': 22  },
    21: { 'bus': 'SWD',   'signal': 'BOOT0',       'cpu_pin': 'BOOT0', 'cpu_pin_no': 999, 'rpi_pin_no': 0   },
    22: { 'bus': 'RSVD',  'signal': 'NBIOT_RST',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 5   },
    23: { 'bus': 'RSVD',  'signal': 'NBIOT_GPIO1', 'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 6   },
    24: { 'bus': 'RSVD',  'signal': 'NBIOT_RXU',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 13  },
    25: { 'bus': 'RSVD',  'signal': 'NBIOT_TXU',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 19  },
    26: { 'bus': 'RSVD',  'signal': 'NBIOT_CTS',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 20  },
    27: { 'bus': 'RSVD',  'signal': 'NBIOT_VINT',  'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 21  }
}

earhart = { 
    1:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    2:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    3:  { 'bus': 'UART',  'signal': 'TXU',         'cpu_pin': 'PA9',   'cpu_pin_no': 9,   'rpi_pin_no': 15  },
    4:  { 'bus': 'UART',  'signal': 'RXU',         'cpu_pin': 'PA10',  'cpu_pin_no': 10,  'rpi_pin_no': 14  },
    5:  { 'bus': 'SPI',   'signal': 'NSS',         'cpu_pin': 'PB12',  'cpu_pin_no': 28,  'rpi_pin_no': 8   },
    6:  { 'bus': 'SPI',   'signal': 'SCK',         'cpu_pin': 'PB13',  'cpu_pin_no': 29,  'rpi_pin_no': 11  },
    7:  { 'bus': 'SPI',   'signal': 'MISO',        'cpu_pin': 'PB14',  'cpu_pin_no': 30,  'rpi_pin_no': 9   },
    8:  { 'bus': 'SPI',   'signal': 'MOSI',        'cpu_pin': 'PB15',  'cpu_pin_no': 31,  'rpi_pin_no': 10  },
    9:  { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    10: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    11: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    12: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 999 },
    13: { 'bus': 'GPIO',  'signal': 'GPIO1',       'cpu_pin': 'PA8',   'cpu_pin_no': 8,   'rpi_pin_no': 4   },
    14: { 'bus': 'I2C',   'signal': 'SCL',         'cpu_pin': 'PB8',   'cpu_pin_no': 24,  'rpi_pin_no': 3   },
    15: { 'bus': 'I2C',   'signal': 'SDA',         'cpu_pin': 'PB9',   'cpu_pin_no': 25,  'rpi_pin_no': 2   },
    16: { 'bus': 'SWD',   'signal': 'SWDIO',       'cpu_pin': 'PA13',  'cpu_pin_no': 13,  'rpi_pin_no': 24  },
    17: { 'bus': 'SWD',   'signal': 'SWCLK',       'cpu_pin': 'PA14',  'cpu_pin_no': 14,  'rpi_pin_no': 25  },
    18: { 'bus': 'SWD',   'signal': 'NRST',        'cpu_pin': 'NRST',  'cpu_pin_no': 999, 'rpi_pin_no': 18  },
    19: { 'bus': 'GPIO',  'signal': 'GPIO2',       'cpu_pin': 'PA11',  'cpu_pin_no': 11,  'rpi_pin_no': 27  },
    20: { 'bus': 'GPIO',  'signal': 'WKUP1',       'cpu_pin': 'PA0',   'cpu_pin_no': 0,   'rpi_pin_no': 22  },
    21: { 'bus': 'SWD',   'signal': 'BOOT0',       'cpu_pin': 'BOOT0', 'cpu_pin_no': 999, 'rpi_pin_no': 0   },
    22: { 'bus': 'RSVD',  'signal': 'LoRa_DIO2',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 5   },
    23: { 'bus': 'RSVD',  'signal': 'LoRa_DIO3',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 6   },
    24: { 'bus': 'RSVD',  'signal': 'LoRa_DIO4',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 13  },
    25: { 'bus': 'RSVD',  'signal': 'LoRa_DIO5',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 19  },
    26: { 'bus': 'RSVD',  'signal': 'LoRa_DIO1',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 20  },
    27: { 'bus': 'RSVD',  'signal': 'LoRa_DIO0',   'cpu_pin': 'N/A',   'cpu_pin_no': 999, 'rpi_pin_no': 21  }
}