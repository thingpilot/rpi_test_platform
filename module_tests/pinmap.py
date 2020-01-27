"""
    file:    pinmap.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python dictionaries listing pin mappings for each Thingpilot module 
"""


wright = { 1:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A'   },
           2:  { 'bus': 'PWR',   'signal': '3V6',         'cpu_pin': 'N/A'   },
           3:  { 'bus': 'UART',  'signal': 'TXU',         'cpu_pin': 'PA2'   },
           4:  { 'bus': 'UART',  'signal': 'RXU',         'cpu_pin': 'PA3'   },
           5:  { 'bus': 'SPI',   'signal': 'NSS',         'cpu_pin': 'PA4'   },
           6:  { 'bus': 'SPI',   'signal': 'SCK',         'cpu_pin': 'PA5'   },
           7:  { 'bus': 'SPI',   'signal': 'MISO',        'cpu_pin': 'PA6'   },
           8:  { 'bus': 'SPI',   'signal': 'MOSI',        'cpu_pin': 'PA7'   },
           9:  { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A'   },
           10: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A'   },
           11: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A'   },
           12: { 'bus': 'PWR',   'signal': 'GND',         'cpu_pin': 'N/A'   },
           13: { 'bus': 'GPIO',  'signal': 'GPIO1',       'cpu_pin': 'PB0'   },
           14: { 'bus': 'I2C',   'signal': 'SCL',         'cpu_pin': 'PA9'   },
           15: { 'bus': 'I2C',   'signal': 'SDA',         'cpu_pin': 'PA10'  },
           16: { 'bus': 'SWD',   'signal': 'SWDIO',       'cpu_pin': 'PA13'  },
           17: { 'bus': 'SWD',   'signal': 'SWCLK',       'cpu_pin': 'PA14'  },
           18: { 'bus': 'SWD',   'signal': 'NRST',        'cpu_pin': 'NRST'  },
           19: { 'bus': 'GPIO',  'signal': 'GPIO2',       'cpu_pin': 'PB1'   },
           20: { 'bus': 'GPIO',  'signal': 'WKUP1',       'cpu_pin': 'PA0'   },
           21: { 'bus': 'SWD',   'signal': 'BOOT0',       'cpu_pin': 'BOOT0' },
           22: { 'bus': 'NBIOT', 'signal': 'NBIOT_RST',   'cpu_pin': 'N/A'   },
           23: { 'bus': 'NBIOT', 'signal': 'NBIOT_GPIO1', 'cpu_pin': 'N/A'   },
           24: { 'bus': 'NBIOT', 'signal': 'NBIOT_RXU',   'cpu_pin': 'N/A'   },
           25: { 'bus': 'NBIOT', 'signal': 'NBIOT_TXU',   'cpu_pin': 'N/A'   },
           26: { 'bus': 'NBIOT', 'signal': 'NBIOT_CTS',   'cpu_pin': 'N/A'   },
           27: { 'bus': 'NBIOT', 'signal': 'NBIOT_VINT',  'cpu_pin': 'N/A'   }
}

earhart = { 1:  { 'bus': 'PWR',   'signal': '3V6',       'cpu_pin': 'N/A'   },
            2:  { 'bus': 'PWR',   'signal': '3V6',       'cpu_pin': 'N/A'   },
            3:  { 'bus': 'UART',  'signal': 'TXU',       'cpu_pin': 'PA9'   },
            4:  { 'bus': 'UART',  'signal': 'RXU',       'cpu_pin': 'PA10'  },
            5:  { 'bus': 'SPI',   'signal': 'NSS',       'cpu_pin': 'PAB12' },
            6:  { 'bus': 'SPI',   'signal': 'SCK',       'cpu_pin': 'PB13'  },
            7:  { 'bus': 'SPI',   'signal': 'MISO',      'cpu_pin': 'PB14'  },
            8:  { 'bus': 'SPI',   'signal': 'MOSI',      'cpu_pin': 'PB15'  },
            9:  { 'bus': 'PWR',   'signal': 'GND',       'cpu_pin': 'N/A'   },
            10: { 'bus': 'PWR',   'signal': 'GND',       'cpu_pin': 'N/A'   },
            11: { 'bus': 'PWR',   'signal': 'GND',       'cpu_pin': 'N/A'   },
            12: { 'bus': 'PWR',   'signal': 'GND',       'cpu_pin': 'N/A'   },
            13: { 'bus': 'GPIO',  'signal': 'GPIO1',     'cpu_pin': 'PA8'   },
            14: { 'bus': 'I2C',   'signal': 'SCL',       'cpu_pin': 'PB8'   },
            15: { 'bus': 'I2C',   'signal': 'SDA',       'cpu_pin': 'PB9'   },
            16: { 'bus': 'SWD',   'signal': 'SWDIO',     'cpu_pin': 'PA13'  },
            17: { 'bus': 'SWD',   'signal': 'SWCLK',     'cpu_pin': 'PA14'  },
            18: { 'bus': 'SWD',   'signal': 'NRST',      'cpu_pin': 'NRST'  },
            19: { 'bus': 'GPIO',  'signal': 'GPIO2',     'cpu_pin': 'PA11'  },
            20: { 'bus': 'GPIO',  'signal': 'WKUP1',     'cpu_pin': 'PA0'   },
            21: { 'bus': 'SWD',   'signal': 'BOOT0',     'cpu_pin': 'BOOT0' },
            22: { 'bus': 'LoRa',  'signal': 'LoRa_DIO2', 'cpu_pin': 'N/A'   },
            23: { 'bus': 'LoRa',  'signal': 'LoRa_DIO3', 'cpu_pin': 'N/A'   },
            24: { 'bus': 'LoRa',  'signal': 'LoRa_DIO4', 'cpu_pin': 'N/A'   },
            25: { 'bus': 'LoRa',  'signal': 'LoRa_DIO5', 'cpu_pin': 'N/A'   },
            26: { 'bus': 'LoRa',  'signal': 'LoRa_DIO1', 'cpu_pin': 'N/A'   },
            27: { 'bus': 'LoRa',  'signal': 'LoRa_DIO0', 'cpu_pin': 'N/A'   }
}