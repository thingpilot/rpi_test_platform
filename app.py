"""
    file:    app.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Flask webserver with real-time functionality provided by SocketIO and eventlet
"""

# Standard library imports
import atexit, datetime
from os import urandom, path, getcwd
from time import sleep

# 3rd-party library imports
import eventlet
from flask import Flask, render_template, escape, request, url_for, redirect, flash, Response
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

# Thingpilot library imports
import app_utils
from python_ocd.targets import stm32l0
from module_tests import hardware_test
from module_provision import provision

# Global Flask and SocketIO objects
ALLOWED_FW_EXTENSIONS = {'bin'}
FIRMWARE_FOLDER = '/python_ocd/firmware'

app = Flask(__name__)

app.config['SECRET_KEY'] = f"{urandom(64)}"
app.config['FIRMWARE_FOLDER'] = FIRMWARE_FOLDER
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def home():
    return render_template("home.html")


def allowed_file(filename, type):
    if type == 'FW':
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_FW_EXTENSIONS


@app.route('/firmware', methods=['POST'])
def firmware_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return Response(status=415)
        
        file = request.files['file']

        if file.filename == '':
            return Response(status=400)

        if allowed_file(file.filename, 'FW'):
            filename = secure_filename(file.filename)
            file.save(f"{getcwd()}{path.join(app.config['FIRMWARE_FOLDER'], filename)}")
            return Response(status=201)
        else:
            return Response(status=400)


@app.route('/developer')
def developer():
    return render_template("developer.html")


@socketio.on('MODULE_PRESENT')
def module_present():
    socketio.emit('js_module_present')


@socketio.on('MODULE_NOT_PRESENT')
def module_not_present():
    socketio.emit('js_module_not_present')


@socketio.on('is_module_present')
def is_module_present():
    socketio.emit('IS_MODULE_PRESENT')


@socketio.on('start_programming')
def start_programming(filename):
    socketio.emit('js_programming_started')
    output_list = list()
    error = False

    with stm32l0.STM32L0() as cpu:
        if cpu:
            for result in cpu.program_bin(filename, stm32l0.STM32L0.PGM_START_ADDRESS):
                if result['success']:
                    if result['message'] != '':
                        if 'enabled\nwrote' in result['message']:
                            messages = result['message'].split('\n')
                            
                            for i in messages[0:2]:
                                output_list.append(f'    {i}\n')
                        else: 
                            output_list.append(f'    {result["message"]}')
                else:
                    output_list.append(f'    Message: {result["message"]} Error: {result["error"]}\n')
                    error = True
                    break

            for message in output_list:     
                socketio.emit('js_programming_progress', message)

            if error:
                socketio.emit('js_programming_error', output_list[-1])
            else:
                socketio.emit('js_programming_success')
        else:
            socketio.emit('js_programming_progress', '    Failed to connect to Tcl server\n')
            socketio.emit('js_programming_error', 'Failed to connect to Tcl server\n')


@socketio.on('get_unique_id')
def get_device_id():
    with stm32l0.STM32L0() as cpu:
        if cpu:
            result = cpu.get_unique_id()

            if result['success']:
                socketio.emit('js_get_unique_id_success', result['message'])
            else:
                socketio.emit('js_get_unique_id_fail', f'Message: {result["message"]} Error: {result["error"]}\n')
        else:
            socketio.emit('js_get_unique_id_fail', f'Failed to connect to Tcl server\n')


@socketio.on('start_provision')
def start_provision(module, url, uid):
    if module is None or url is None or uid is None:
        return Response(status=400)

    with stm32l0.STM32L0() as cpu:
        if cpu:
            cpu.init()
            cpu.reset_run()
        else:
            socketio.emit('js_fail_init_cpu_provision')
            return Response(status=500)

    prov = provision.ThingpilotProvisioner(module.lower(), url, uid)

    prov_bool = False

    for result in prov.provision():
        socketio.emit('js_programming_progress', result['message'])


@socketio.on('begin_test')
def begin_test(module):
    if module is None:
        return Response(status=400)

    with stm32l0.STM32L0() as cpu:
        if cpu:
            cpu.init()
            cpu.reset_run()
        else:
            socketio.emit('js_fail_init_cpu_test')
            return Response(status=500)

    hw = hardware_test.HardwareTest(module.lower())
    test_bool = True
    
    for result in hw.run_test():
        if not result['success']:
            test_bool = False

        if result['message'].lower() == 'gpio':

            test_pass = 'PASSED <i class="fas fa-check-circle"></i>'
            
            for test_result in result['results']['results']:
                pin = 'Pin {: <2} -'.format(test_result["pin"])

                if test_result["high"]:
                    high_icon = '<i class="fas fa-check-circle"></i>'
                else:
                    high_icon = '<i class="fas fa-times-circle"></i>'

                if test_result["low"]:
                    low_icon = '<i class="fas fa-check-circle"></i>'
                else:
                    low_icon = '<i class="fas fa-times-circle"></i>'

                high = f'Assert: {high_icon}'
                low = f'Deassert: {low_icon}'

                row = [ pin, high, low ]

                if test_result["high"] == False or test_result["low"] == False:
                    test_pass = 'FAILED <i class="fas fa-times-circle"></i>'

                socketio.emit('js_programming_progress', '        {: <8} {: <14} {: <20}\n'.format(*row))

            socketio.emit('js_programming_progress', f'    HW Test (GPIO) - {test_pass}. Took: {result["results"]["time_taken"]}ms\n')
        else:
            socketio.emit('js_programming_progress', result['message'])
            socketio.sleep(0.1)
        
    socketio.emit('js_test_complete', test_bool)


def exit_handler():
    socketio.emit('SHUTDOWN')
    print(f"{datetime.datetime.now()} app.py: *** TERMINATING APPLICATION ***")
    exit()


if __name__ == '__main__':
    atexit.register(exit_handler)

    try:
        socketio.run(app, host=app_utils.get_ip_address(), port=80, debug=True)
    except KeyboardInterrupt:
        sys.exit()