import time

import pika
import requests
from flask import url_for

CREDENTIAL_KEY = "0806444524"
MY_NPM = "1606917550"
RABBIT_HOST = "152.118.148.95"
RABBIT_PORT = 5672

PROGRESS_TEMPLATE = "Downloading {:s}: {:.2f}%"

DIR_PATH = '/home/cots/'


def execute(url, routing_key):
    send_message("Initiate download {:s}".format(url), routing_key)
    download_file(url, routing_key)


def download_file(url, routing_key):
    try:
        response = requests.get(url, stream=True)
    except ConnectionError:
        send_message("Connection failed to: {:s} ".format(url), routing_key)
        return

    response.raise_for_status()

    filename = url.split('/')[-1]
    file = open(DIR_PATH + filename, 'wb')
    size = response.headers.get('content-length')

    if size is None:  # no content length header
        file.write(response.content)
    else:
        written = 0
        for chunk in response.iter_content(chunk_size=512):
            written += len(chunk)
            progress = (written / int(size)) * 100
            send_message(PROGRESS_TEMPLATE.format(url, progress), routing_key)
            file.write(chunk)

    response.close()
    file.close()
    send_message("Download finished: %s".format(url_for("retrieve", filename=filename)), routing_key)


def send_message(message, route):
    time.sleep(0.6)
    cred = pika.PlainCredentials(username=CREDENTIAL_KEY, password=CREDENTIAL_KEY)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT,
                                  virtual_host="/" + CREDENTIAL_KEY, credentials=cred)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=MY_NPM, exchange_type='direct')
    channel.basic_publish(exchange=MY_NPM, routing_key=route, body=message)
    connection.close()
    time.sleep(0.6)
