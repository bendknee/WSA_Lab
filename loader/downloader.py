import json
import os
import pathlib

import requests

from utils.broker import CHANNEL_PROGRESS

COMPRESSOR_PORT = os.getenv('LAW_COMPRESS_PORT', '20016')
ROOT_DIR = os.getenv('LAW_ROOT_DIR', '/law')
KB = 1024


def download(broker, url, process_id):
    pathlib.Path(os.path.join(ROOT_DIR, process_id)).mkdir(parents=True, exist_ok=True, mode=0o744)
    filepath = get_file_path(url, process_id)
    file = open(filepath, 'wb')
    try:
        response = requests.get(url, stream=True, timeout=60*10)
        size = response.headers.get('content-length')

        written = 0
        for chunk in response.iter_content(chunk_size=16*KB):
            file.write(chunk)
            written += len(chunk)
            if size is None:
                broker.send(jsonify(url, filepath, humanize_byte(written)), CHANNEL_PROGRESS.format(process_id))
            else:
                progress = "{:d}%".format(int(written / int(size) * 100))
                broker.send(jsonify(url, filepath, progress), CHANNEL_PROGRESS.format(process_id))

        response.close()
        file.close()
        send_metadata(process_id, filepath, written)
    except IOError:
        file.close()
        os.remove(filepath)
        broker.send(jsonify(url, filepath, "FAIL"), CHANNEL_PROGRESS.format(process_id))


def get_file_path(url, process_id):
    filename = url.split('/')[-1]
    name_only = filename
    file_ext = str()
    if '.' in filename:
        ext_split = filename.rsplit('.', 1)
        name_only = ext_split[0]
        file_ext = '.' + ext_split[1].lower()

    filepath = os.path.join(ROOT_DIR, process_id, "{:s}{:s}".format(name_only, file_ext))
    uniq = 1
    while os.path.exists(filepath):
        filepath = os.path.join(ROOT_DIR, process_id, "{:s}_({:d}){:s}".format(name_only, uniq, file_ext))
        uniq += 1
    return filepath


def jsonify(url, filepath, progress):
    url = url.rsplit('/', 1)[0]
    filename = filepath.rsplit('/', 1)[1]
    jeson = {'url': "{:s}/{:s}".format(url, filename), 'progress': progress}
    return json.dumps(jeson)


def humanize_byte(byte):
    if byte < KB:
        return "{:d} B".format(byte)
    elif byte < KB**2:
        return "{:.2f} KB".format(byte/KB)
    else:
        return "{:.2f} MB".format(byte/(KB**2))


def send_metadata(process_id, filepath, size):
    filename = filepath.rsplit('/', 1)[-1]
    payload = {'process_id': process_id, 'filename': filename, 'size': str(size)}
    requests.post("http://localhost:{:s}/meta".format(COMPRESSOR_PORT), data=payload)
