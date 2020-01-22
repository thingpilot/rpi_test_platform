"""
    file:    ocd_wrapper.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Python wrapper around OpenOCD. Parses output and relays back to webserver 
             running in app.py
"""

# Standard library imports
import datetime, os, subprocess, time

# 3rd-party library imports
import socketio

# Global socketIO object
sio = socketio.Client()


def get_ip_address():
    ip = subprocess.check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


def make_config_file(firmware_filename):
    config_file_content = [ 'bindto 0.0.0.0',
                            'source [find interface/raspberrypi2-native.cfg]',
                            'transport select swd',
                            'set WORKAREASIZE 0x2000',
                            'source [find target/stm32l0.cfg]',
                            'reset_config srst_only',
                            'adapter_nsrst_delay 100',
                            'adapter_nsrst_assert_width 100',
                            'init',
                            'reset',
                            'halt',
                            f'flash write_image erase firmware/{firmware_filename} 0x08000000',
                            f'verify_image firmware/{firmware_filename} 0x08000000',
                            'init',
                            'reset',
                            'targets'
                          ]
    
    print(f"{datetime.datetime.now()} ocd_wrapper.py: Created configuration file using {firmware_filename}")
    
    with open('openocd.cfg', 'w') as config_file:
        config_file.write("\n".join(config_file_content))


@sio.on('START_PROGRAMMING')
def program_and_verify(firmware_filename):
    default_working_directory = os.getcwd()
    os.chdir(f"{default_working_directory}/ocd")

    make_config_file(firmware_filename)

    print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming started using {firmware_filename}")
    sio.emit('programming_started')

    try:
        process = subprocess.Popen(['sudo', 'openocd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        os.system(f"sudo pkill -9 openocd")
        os.chdir(default_working_directory)

        print(f"{datetime.datetime.now()} ocd_wrapper.py: OpenOCD error: {e}")

    for line in process.stderr:
        line_decoded = line.decode('utf-8')
        line_array = line_decoded.split(' ')
        
        sio.emit('programming_progress', line_decoded)  

        if 'checksum' in line_array and 'mismatch' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - checksum mismatch")
            sio.emit('programming_verification_fail')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'auto_probe' in line_array and 'failed' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - flash probe failed, likely target not halted")
            sio.emit('programming_flash_probe_failed')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'failed' in line_array and 'erasing' in line_array and 'sectors' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - failed erasing flash")
            sio.emit('programming_fail_erase_flash')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'Target' in line_array and 'not' in line_array and 'halted' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - target not halted")
            sio.emit('programming_target_not_halted')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'stm32l0.cpu' in line_array and 'halted\n' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - unknown")
            sio.emit('programming_unknown_error')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'stm32l0.cpu' in line_array and 'unknown\n' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - unknown")
            sio.emit('programming_unknown_error')
            os.system(f"sudo pkill -9 openocd")
            break

        if 'stm32l0.cpu' in line_array and 'running\n' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming success")
            sio.emit('programming_success')
            os.system(f"sudo pkill -9 openocd")
            break

        if '4444' in line_array and 'telnet' in line_array:
            print(f"{datetime.datetime.now()} ocd_wrapper.py: Programming error - unknown")
            sio.emit('programming_unknown_error')
            os.system(f"sudo pkill -9 openocd")
            break

    os.chdir(default_working_directory)
    

if __name__ == '__main__':
    sio.connect(f"http://{get_ip_address()}:80")

    try:
        while True:
            time.sleep(1e6)
    except KeyboardInterrupt:
        print(f"{datetime.datetime.now()} ocd_wrapper.py: Terminating OpenOCD interface")
        exit()