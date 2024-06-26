import os
import socket
from flask import Flask, render_template, request, send_from_directory
from flask_dropzone import Dropzone

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'uploads'), exist_ok=True)
app = Flask(__name__)
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    DROPZONE_MAX_FILE_SIZE=1024 * 1024,  # MB (1024 * 1024 == 1TB)
    DROPZONE_TIMEOUT=1000 * 60 * 60 * 24,  # millisecond (1000 * 60 * 60 * 24 == 1day)
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='',
    DROPZONE_SERVE_LOCAL=True

)
dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('upload.html')


@app.route('/download', methods=['GET'])
def download():
    files = os.listdir(app.config['UPLOADED_PATH'])
    return render_template('download.html', files=files)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOADED_PATH'], filename, as_attachment=True)


if __name__ == '__main__':
    hostname = socket.gethostname()
    ipv4_address = socket.gethostbyname(hostname)
    app.run(f'{ipv4_address}', port=1000, debug=True)
