from flask import Flask, render_template, request, Response

from fend.api import relay_file_to_backend

FILE_ARG = "file"

fend = Flask(__name__)
fend.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


@fend.route('/')
def index():
    return render_template('index.html')


@fend.route('/upload', methods=['POST'])
def uploader():
    response = relay_file_to_backend(request.files.getlist(FILE_ARG))

    return Response(response.text, status=response.status_code, content_type='application/json')


if __name__ == '__main__':
    fend.run()
