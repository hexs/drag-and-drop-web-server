import os
from flask import Flask, render_template, request, send_from_directory
from flask_dropzone import Dropzone

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'uploads'), exist_ok=True)
app = Flask(__name__)
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    DROPZONE_MAX_FILE_SIZE=1024,
    DROPZONE_TIMEOUT=5 * 60 * 1000,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE=''

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
    app.run('192.168.225.137', debug=True)
