import os
import zipfile
from datetime import datetime

from flask import Flask, abort, Response, request, send_from_directory
from werkzeug.utils import secure_filename

from zipper.api import authorized

UPLOAD_DIR = '/home/fs/zip'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}

AUTHORIZATION_ARG = "Authorization"
FILE_ARG = "file"

zipper = Flask(__name__)
zipper.config['UPLOAD_FOLDER'] = UPLOAD_DIR
zipper.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


@zipper.route('/api/zip')
def zippa():
    authenticate()

    if FILE_ARG not in request.files:
        abort(Response("No 'file' argument found", status=400))
    if request.files[FILE_ARG].filename == '':
        abort(Response("No selected file", status=400))

    clean_up()
    zip_name = zip_files(request.files.getlist(FILE_ARG))
    return send_from_directory(zipper.config['UPLOAD_FOLDER'], zip_name)


def authenticate():
    if AUTHORIZATION_ARG not in request.headers:
        abort(Response("No token provided (BEARER_TOKEN == NaN)", status=401))
    if not authorized(request.headers[AUTHORIZATION_ARG]):
        abort(Response("Invalid token or expired token", status=401))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def zip_files(files):

    zip_name = "{:s}.zip".format(str(datetime.now().strftime('%Y%m%d%H%M%S')))
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for file in files:
        if allowed_file(file.filename):
            clean_filename = secure_filename(file.filename)
            file.save(os.path.join(zipper.config['UPLOAD_FOLDER'], clean_filename))
            zipf.write(os.path.join(zipper.config['UPLOAD_FOLDER'], clean_filename))

    zipf.close()

    return zip_name


def clean_up():
    for dirpath, _, filenames in os.walk(zipper.config['UPLOAD_FOLDER']):
        for file in filenames:
            os.remove(os.path.join(dirpath, file))


if __name__ == '__main__':
    zipper.run()
