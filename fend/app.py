from flask import Flask, render_template, request, json, redirect, url_for

from fend import api
from fend.api import relay_file_to_backend

FILE_ARG = "file"
SUCCESS_UPLOAD_KEY = "total_saved"

fend = Flask(__name__)
fend.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


@fend.route('/')
def index():
    return render_template('index.html')


@fend.route('/receiver/<uuid:route>', methods=['GET'])
def receiver(route):
    return render_template('receiver.html', route=route)


@fend.route('/upload', methods=['POST'])
def uploader():
    response = relay_file_to_backend(request.files.getlist(FILE_ARG))
    response_dict = json.loads(response.text)
    return redirect(url_for("receiver", route=response_dict[api.ROUTING_KEY]))


if __name__ == '__main__':
    fend.run()
