import multiprocessing
import uuid

from flask import Flask, render_template, request, abort, Response, redirect, url_for, send_from_directory

import daemon

FILENAME_ARG = "filename"
URL_ARG = "link"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = daemon.DIR_PATH


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/progress/<uuid:route>', methods=['GET'])
def progress(route):
    return render_template('progress.html', route=route)


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get(URL_ARG)
    if url is None:
        abort(Response("`{:s}` argument required".format(URL_ARG), status=400))
    if len(url) == 0:
        abort(Response("`{:s}` argument is empty".format(URL_ARG), status=400))

    routing_key = str(uuid.uuid4())
    execute_daemon(url, routing_key, request.host_url + url_for("retrieve"))

    return redirect(url_for("progress", route=routing_key))


@app.route('/retrieve/', methods=['GET'])
def retrieve():
    filename = request.args.get(FILENAME_ARG)
    if filename is None:
        abort(Response("`{:s}` argument required".format(FILENAME_ARG), status=400))
    if len(filename) == 0:
        abort(Response("`{:s}` argument is empty".format(FILENAME_ARG), status=400))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def execute_daemon(url, routing_key, host_address):
    pool = multiprocessing.Pool()
    pool.apply_async(daemon.execute, (url, routing_key, host_address))
    pool.close()


if __name__ == '__main__':
    app.run()
