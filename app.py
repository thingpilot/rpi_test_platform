"""
    file:    app.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Flask webserver with real-time functionality provided by SocketIO and eventlet
"""

# Standard library imports
import atexit, datetime, requests, subprocess, time
from os import urandom, path, getcwd
from subprocess import check_output

# 3rd-party library imports
import eventlet
from flask import Flask, render_template, request, Response
from flask_socketio import Namespace, SocketIO
from werkzeug.utils import secure_filename


# Global Flask and SocketIO objects
ALLOWED_FW_EXTENSIONS = {'bin'}
FIRMWARE_FOLDER = '/python_ocd/firmware'

app = Flask(__name__)

app.config['SECRET_KEY'] = f"{urandom(64)}"
app.config['FIRMWARE_FOLDER'] = FIRMWARE_FOLDER
socketio = SocketIO(app, async_mode='eventlet', logger=True)


class DeviceNamespace(Namespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._can_test = False
        self._can_provision = False

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass
    
    def on_get_unique_id(self):
        socketio.emit('get_unique_id', namespace='/STM32L0Namespace')

    def on_get_unique_id_progress(self, data):
        socketio.emit('get_unique_id_progress', data, namespace='/WebAppNamespace')

    def on_program_bin(self, binary):
        socketio.emit('program_bin', binary, namespace='/STM32L0Namespace')

    def on_program_bin_progress(self, data):
        if data['message'] != '':
            if 'enabled\nwrote' in data['message']:
                messages = data['message'].split('\n')

                for msg in messages[0:2]:
                    socketio.emit('program_bin_progress', { 'success': True, 'message': msg, 'error': ''}, namespace='/WebAppNamespace')
            elif 'verified' in data['message']:
                msg = data['message'].split('\n')[0]
                socketio.emit('program_bin_progress', { 'success': True, 'message': msg, 'error': ''}, namespace='/WebAppNamespace')
            else:
                socketio.emit('program_bin_progress', data, namespace='/WebAppNamespace')

    def on_run_test(self, module):
        self._can_test = False

        socketio.emit('run_test', namespace='/STM32L0Namespace')

        start_time = time.time()

        while not self._can_test:
            socketio.sleep(0.1)

            if time.time() > (start_time + 1000):
                socketio.emit('run_test_progress', { 'success': False, 'message': 'Failed to place target CPU into control mode', 'error': 'Timeout'}, namespace='/WebAppNamespace')

        if self._can_test:
            socketio.emit('run_test', module.lower(), namespace='/HWTestNamespace')

    def on_run_test_progress(self, data):
        if 'Target CPU running' in data['message']:
            self._can_test = True 

        socketio.emit('run_test_progress', data, namespace='/WebAppNamespace')  

    def on_run_provision(self, module, url, uid):
        self._can_provision = False

        socketio.emit('run_provision', namespace='/STM32L0Namespace')

        start_time = time.time()

        while not self._can_provision:
            socketio.sleep(0.1)

            if time.time() > (start_time + 1000):
                socketio.emit('run_provision_progress', { 'success': False, 'message': 'Failed to place target CPU into control mode', 'error': 'Timeout'}, namespace='/WebAppNamespace')
        
        if self._can_provision:
            socketio.emit('run_provision', (module, url, uid), namespace='/ProvisionerNamespace')

    def on_run_provision_progress(self, data):
        if 'Target CPU running' in data['message']:
            self._can_provision = True 

        socketio.emit('run_provision_progress', data, namespace='/WebAppNamespace')  
        

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


def exit_handler():
    socketio.emit('SHUTDOWN')
    print(f"{datetime.datetime.now()} app.py: *** TERMINATING APPLICATION ***")
    exit()


def get_ip_address():
    ip = check_output(['hostname', '-I'])
    ip = ip.split()[0]
    ip = ip.decode('utf-8')

    return ip


if __name__ == '__main__':
    atexit.register(exit_handler)

    socketio.on_namespace(DeviceNamespace('/DeviceNamespace'))

    try:      
        socketio.run(app, host=get_ip_address(), port=80, debug=True)
    except KeyboardInterrupt:
        sys.exit()