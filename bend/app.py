import multiprocessing
import os

from flask import Flask, request, abort, Response, json
from werkzeug.utils import secure_filename

from bend import daemon

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}
FAILED_UPLOAD_KEY = "upload_failures"
FILE_ARG = "file"
ROUTING_KEY = "X_ROUTING_KEY"
STORAGE_DIR = '/home/daemon'
SUCCESS_UPLOAD_KEY = "total_saved_files"

bend = Flask(__name__)
bend.config['UPLOAD_FOLDER'] = STORAGE_DIR
bend.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


@bend.route('/')
def index():
    return Response("Hi", 200)


@bend.route('/compress', methods=['POST'])
def store_file():
    if FILE_ARG not in request.files:
        abort(Response("No 'file' argument found", status=400))
    if request.files[FILE_ARG].filename == '':
        abort(Response("No file selected", status=400))

    response = save_files(request.files.getlist(FILE_ARG))

    execute_daemon(request.headers[ROUTING_KEY])

    if response[SUCCESS_UPLOAD_KEY] == 0:
        return Response(", ".join(response[FAILED_UPLOAD_KEY]), status=400)
    else:
        return Response(json.dumps(response), status=200, content_type='application/json')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_files(files):
    response = {SUCCESS_UPLOAD_KEY: 0}

    for file in files:
        if not allowed_file(file.filename):
            if FAILED_UPLOAD_KEY not in response:
                response[FAILED_UPLOAD_KEY] = list()
            response[FAILED_UPLOAD_KEY].append("Can't save {:s}: .{:s} extension is not allowed"
                                               .format(file.filename, file.filename.rsplit('.', 1)[1]))
        else:
            try:
                clean_filename = secure_filename(file.filename)
                file.save(os.path.join(bend.config['UPLOAD_FOLDER'], clean_filename))
                response[SUCCESS_UPLOAD_KEY] += 1
            except:
                if FAILED_UPLOAD_KEY not in response:
                    response[FAILED_UPLOAD_KEY] = list()
                response[FAILED_UPLOAD_KEY].append("Exception occurred when saving {:s}".format(file.filename))

    return response


def execute_daemon(routing_key):
    pool = multiprocessing.Pool()
    pool.apply_async(daemon.execute, (routing_key,))
    pool.close()


if __name__ == '__main__':
    bend.run()
