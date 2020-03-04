import os

from flask import Flask, request, abort, Response, send_from_directory, jsonify
from werkzeug.utils import secure_filename

from fs.api import authorized

UPLOAD_DIR = '/home/fs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}
FILE_ARG = "file"

DOWNLOAD_LINK_KEY = "download_link"
FAILED_UPLOADS_KEY = "failed_uploads"

fs = Flask(__name__)
fs.config['UPLOAD_FOLDER'] = UPLOAD_DIR
fs.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


@fs.route('/api/upload', methods=['POST'])
def upload():
    bearer_token = request.headers["Authorization"]
    if bearer_token is None or bearer_token == '':
        abort(Response("No token provided (BEARER_TOKEN == NaN)", status=401))
    if not authorized(bearer_token):
        abort(Response("Invalid token or expired token", status=401))

    if FILE_ARG not in request.files:
        abort(Response("No 'file' argument found", status=400))
    if request.files[FILE_ARG].filename == '':
        abort(Response("No selected file", status=400))

    response = save_files(request.files.getlist(FILE_ARG))

    if len(response[DOWNLOAD_LINK_KEY]) == 0:
        return Response(jsonify(response), status=400)
    else:
        return Response(jsonify(response), status=200)


@fs.route('/api/download/<filename>', methods=['GET'])
def download(filename):
    bearer_token = request.headers["Authorization"]
    if bearer_token is None or bearer_token == '':
        abort(Response("No token provided (BEARER_TOKEN == NaN)", status=401))
    if not authorized(bearer_token):
        abort(Response("Invalid token or expired token", status=401))
    return send_from_directory(fs.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_files(files):
    response = {DOWNLOAD_LINK_KEY: list(),
                FAILED_UPLOADS_KEY: list()}

    for file in files:
        if not allowed_file(file.filename):
            response[FAILED_UPLOADS_KEY].append("{:s} extension is not allowed".format(file.filename.rsplit('.', 1)[1]))
        else:
            clean_filename = secure_filename(file.filename)
            file.save(os.path.join(fs.config['UPLOAD_FOLDER'], clean_filename))
            response[DOWNLOAD_LINK_KEY].append(request.host_url + "/api/download/" + clean_filename)

    return response


if __name__ == '__main__':
    fs.run()
