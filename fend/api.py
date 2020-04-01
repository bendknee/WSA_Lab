import uuid

import requests as r

BEND_URL = "127.0.0.1"
BEND_PORT = "20018"
BEND_URI = "compress"
FILE_ARG = "file"
ROUTING_KEY = "X_ROUTING_KEY"


def relay_file_to_backend(files):
    url = "http://{:s}:{:s}/{:s}".format(BEND_URL, BEND_PORT, BEND_URI)
    all_files = [(FILE_ARG, (f.filename, f.stream, f.mimetype)) for f in files]
    headers = {ROUTING_KEY: str(uuid.uuid4())}
    req = r.post(url, files=all_files, headers=headers)
    return req
