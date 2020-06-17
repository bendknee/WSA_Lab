import json
import multiprocessing
import os

import requests

from loader.downloader import download
from utils.broker import BrokerUtils, MODE_DIRECT, MODE_TOPIC, CHANNEL_DOWNLOAD

COMPRESSOR_PORT = os.getenv('LAW_COMPRESS_PORT', '20016')

receiver = BrokerUtils(MODE_DIRECT)
producer = BrokerUtils(MODE_TOPIC)


def start_consume():
    receiver.receive(CHANNEL_DOWNLOAD, handler)


def handler(ch, method, properties, body):
    payload = body.decode("UTF-8")
    jeson = json.loads(payload)

    if 'process_id' not in jeson:
        return

    process_id = jeson['process_id']

    if 'url' in jeson:
        # download asynchronously
        url = jeson['url']
        pool = multiprocessing.Pool()
        pool.apply_async(download, (producer, url, process_id,))
        pool.close()
    elif 'client_ip' in jeson:
        notify_compressor(jeson)


def notify_compressor(data):
    payload = {'process_id': data['process_id'], 'client_ip': data['client_ip'], 'host_ip': data['host_ip']}
    requests.post("http://localhost:{:s}/compress".format(COMPRESSOR_PORT), data=payload)
