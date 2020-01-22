"""
    file:    app.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Flask webserver with real-time functionality provided by SocketIO and eventlet
"""

# Standard library imports
import atexit, datetime
from os import urandom, path, getcwd

# 3rd-party library imports
import eventlet
from flask import Flask, render_template, escape, request, url_for, redirect, flash, Response
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

# Thingpilot library imports
import app_utils
from ocd import ocd_wrapper

# Global Flask and SocketIO objects
ALLOWED_FW_EXTENSIONS = {'bin'}
ALLOWED_TEST_EXTENSIONS = {'py'}
FIRMWARE_FOLDER = '/ocd/firmware'
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
    socketio.emit('START_PROGRAMMING', filename)


@socketio.on('programming_started')
def programming_started():
    socketio.emit('js_programming_started')


@socketio.on('programming_progress')
def programming_progress(line):
    socketio.emit('js_programming_progress', line)


@socketio.on('programming_success')
def programming_success():
    socketio.emit('js_programming_success')


@socketio.on('programming_verification_fail')
def programming_verification_error():
    socketio.emit('js_programming_verification_fail')


@socketio.on('programming_flash_probe_failed')
def programming_flash_probe_failed():
    socketio.emit('js_programming_flash_probe_failed')


@socketio.on('programming_fail_erase_flash')
def programming_fail_erase_flash():
    socketio.emit('js_programming_erase_flash')


@socketio.on('programming_target_not_halted')
def programming_target_not_halted():
    socketio.emit('js_programming_target_not_halted')


@socketio.on('programming_unknown_error')
def programming_unknown_error():
    socketio.emit('js_programming_unknown_error')


def exit_handler():
    socketio.emit('SHUTDOWN')
    print(f"{datetime.datetime.now()} app.py: *** TERMINATING APPLICATION ***")
    exit()


if __name__ == '__main__':
    atexit.register(exit_handler)
    socketio.run(app, host=app_utils.get_ip_address(), port=80, debug=True)