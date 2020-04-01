from flask import Flask, render_template, request, Response, abort, json

from fend.api import relay_file_to_backend

FILE_ARG = "file"

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
    routing_key, response = relay_file_to_backend(request.files.getlist(FILE_ARG))
    if response.status_code != 200:
        abort(Response(response.text, status=response.status_code))

    return render_template('redirect.html', route_key=routing_key, bend_resp=json.loads(response.text))


if __name__ == '__main__':
    fend.run()
