import os
import shutil
import subprocess
import time
import zipfile

from utils.broker import CHANNEL_COMPRESS

METAFILE_NAME = 'meta.txt'
NGINX_PORT = os.getenv('LAW_NGINX_PORT', '20010')
ROOT_DIR = os.getenv('LAW_ROOT_DIR', '/law')
LINK_AGE = os.getenv('LAW_LINK_AGE', '20')
WAITING_TIMEOUT = 10


def execute(process_id, host_ip, client_ip, broker):
    wait_download(process_id, broker)
    zip_files(process_id, broker)
    share_link(process_id, host_ip, client_ip, broker)
    clean_up(process_id)


def wait_download(process_id, broker):
    start_time = int(time.time())
    finished = False
    while not finished:
        if int(time.time()) >= start_time + WAITING_TIMEOUT * 60:
            broker.send("TIMEOUT: download too long", CHANNEL_COMPRESS.format(process_id))
            exit(1)

        broker.send("waiting download to finish...", CHANNEL_COMPRESS.format(process_id))
        finished = True
        root, _, files = next(os.walk(os.path.join(ROOT_DIR, process_id)))
        meta = get_metadata(process_id)
        for file in files:
            if file == METAFILE_NAME:
                continue
            if file not in meta or os.path.getsize(os.path.join(root, file)) != meta.get(file):
                finished = False

    broker.send("starting compression...", CHANNEL_COMPRESS.format(process_id))
    os.remove(os.path.join(ROOT_DIR, process_id, METAFILE_NAME))


def get_metadata(process_id):
    metadata = dict()
    try:
        metafile = open(os.path.join(ROOT_DIR, process_id, METAFILE_NAME), 'r')
    except IOError:
        return metadata

    for line in metafile.readlines():
        line = line.rstrip('\n')
        data = line.split(";=;")
        metadata[data[0]] = int(data[1])

    return metadata


def zip_files(process_id, broker):
    zip_name = "{:s}.zip".format(process_id)
    zipf = zipfile.ZipFile(os.path.join(ROOT_DIR, zip_name), 'w', zipfile.ZIP_DEFLATED)
    root, _, files = next(os.walk(os.path.join(ROOT_DIR, process_id)))
    for i in range(len(files)):
        zipf.write(os.path.join(root, files[i]), arcname=files[i])
        broker.send("{:d}%".format(int(i / len(files) * 100)), CHANNEL_COMPRESS.format(process_id))

    broker.send("100%", CHANNEL_COMPRESS.format(process_id))
    zipf.close()


def share_link(process_id, host_ip, client_ip, broker):
    template = "{:d}/{:s}.zip{:s} secret"
    link_age = int(time.time()) + 60 * int(LINK_AGE)

    callsign = template.format(link_age, process_id, client_ip)
    biner = subprocess.check_output(["openssl", "md5", "-binary"], input=callsign.encode("UTF-8"))
    md5 = subprocess.check_output(["openssl", "base64"], input=biner)
    md5 = md5.decode("UTF-8").replace('/', '_').replace('=', '').strip('\n')

    url = "{:s}:{:s}/{:s}.zip?md5={:s}&expires={:d}"
    host_ip = host_ip.rsplit(':', 1)[0]
    broker.send(url.format(host_ip, NGINX_PORT, process_id, md5, link_age), CHANNEL_COMPRESS.format(process_id))


def clean_up(process_id):
    shutil.rmtree(os.path.join(ROOT_DIR, process_id), ignore_errors=True)

