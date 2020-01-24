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

# Global Flask and SocketIO objects
ALLOWED_FW_EXTENSIONS = {'bin'}
ALLOWED_TEST_EXTENSIONS = {'py'}
FIRMWARE_FOLDER = '/python_ocd/firmware'
TEST_FOLDER = '/module_tests'

app = Flask(__name__)
app.config['SECRET_KEY'] = f"{urandom(64)}"
app.config['FIRMWARE_FOLDER'] = FIRMWARE_FOLDER
app.config['TEST_FOLDER'] = TEST_FOLDER
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def home():
    return render_template("home.html")


def allowed_file(filename, type):
    if type == 'FW':
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_FW_EXTENSIONS
    elif type == 'TEST':
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_TEST_EXTENSIONS


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


@app.route('/test', methods=['POST'])
def test_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return Response(status=415)

        file = request.files['file']

        if file.filename == '':
            return Response(status=400)

        if allowed_file(file.filename, 'TEST'):
            filename = secure_filename(file.filename)
            file.save(f"{getcwd()}{path.join(app.config['TEST_FOLDER'], filename)}")
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
                        output_list.append(result['message'])
                else:
                    output_list.append(f'Message: {result["message"]} Error: {result["error"]}\n')
                    error = True
                    break

            for message in output_list:     
                socketio.emit('js_programming_progress', message)

            if error:
                socketio.emit('js_programming_error', output_list[-1])
            else:
                socketio.emit('js_programming_success')
        else:
            socketio.emit('js_programming_progress', 'Failed to connect to Tcl server\n')
            socketio.emit('js_programming_error', 'Failed to connect to Tcl server\n')


def exit_handler():
    socketio.emit('SHUTDOWN')
    sleep(0.3)
    print(f"{datetime.datetime.now()} app.py: *** TERMINATING APPLICATION ***")
    exit()


if __name__ == '__main__':
    atexit.register(exit_handler)
    socketio.run(app, host=app_utils.get_ip_address(), port=80, debug=True)