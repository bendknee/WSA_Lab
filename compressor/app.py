import multiprocessing
import os

from flask import Flask, request, redirect, url_for, abort, Response

from compressor.squeezer import execute
from utils.broker import BrokerUtils, MODE_TOPIC

app = Flask(__name__)
METAFILE_NAME = 'meta.txt'
ROOT_DIR = os.getenv('LAW_ROOT_DIR', '/law')


@app.route('/', methods=['POST'])
def index():
    return redirect(url_for("squeeze"))


@app.route('/compress', methods=['POST'])
def squeeze():
    process_id = request.values.get('process_id')
    if process_id is None:
        abort(Response("'process_id' data required", status=400))

    client_ip = request.values.get('client_ip')
    host_ip = request.values.get('host_ip')

    broker = BrokerUtils(MODE_TOPIC)
    pool = multiprocessing.Pool()
    pool.apply_async(execute, (process_id, host_ip, client_ip, broker))
    pool.close()

    return Response(status=200)


@app.route('/meta', methods=['POST'])
def meta():
    process_id = request.values.get('process_id')
    filename = request.values.get('filename')
    size = request.values.get('size')
    if process_id is None:
        abort(Response("'process_id' data required", status=400))
    if filename is None:
        abort(Response("'filename' data required", status=400))
    if size is None:
        size = '0'

    metafile = open(os.path.join(ROOT_DIR, process_id, METAFILE_NAME), 'a')
    metafile.write("{:s};=;{:s}\n".format(filename, size))
    metafile.close()

    return Response(status=200)


if __name__ == '__main__':
    app.run()
