import requests as r

BEND_URL = "127.0.0.1"
BEND_PORT = "20018"
BEND_URI = "compress"
FILE_ARG = "file"


def relay_file_to_backend(files):
    url = "{:s}:{:s}/{:s}".format(BEND_URL, BEND_PORT, BEND_URI)
    all_files = [(FILE_ARG, (f.filename, f.stream, f.mimetype)) for f in files]
    req = r.post(url, files=all_files)
    return req
