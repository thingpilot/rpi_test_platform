"""
    file:    app.py
    version: 0.1.0
    author:  Adam Mitchell
    brief:   Flask webserver with real-time functionality provided by SocketIO and eventlet
"""

# Standard library imports
from os import urandom, path, getcwd

# 3rd-party library imports
import eventlet
from flask import Flask, render_template, escape, request, url_for, redirect, flash, Response
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

# Thingpilot library imports
import app_utils

# Global Flask and SocketIO objects
ALLOWED_EXTENSIONS = {'bin'}
UPLOAD_FOLDER = '/ocd/firmware'

app = Flask(__name__)
app.config['SECRET_KEY'] = f"{urandom(64)}"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app, async_mode='eventlet')


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def home():
    return render_template("home.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/firmware', methods=['POST'])
def firmware_upload():
    if request.method == 'POST':
        print("POST POST POST POST POST")
        print(getcwd())

        if 'file' not in request.files:
            flash('File not in request.files!', 'danger')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(f"{getcwd()}{path.join(app.config['UPLOAD_FOLDER'], filename)}")
            print(path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(f"{getcwd()}{path.join(app.config['UPLOAD_FOLDER'], filename)}")
            return Response(status=201)


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


@socketio.on('firmware_upload')
def handle_firmware_upload(firmware):
    print(firmware)


if __name__ == '__main__':
    socketio.run(app, host=app_utils.get_ip_address(), port=80, debug=True)