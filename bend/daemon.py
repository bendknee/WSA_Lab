import shutil
import time
from os import walk
from os.path import join

import pika

CREDENTIAL_KEY = "0806444524"
MY_NPM = "1606917550"
RABBIT_HOST = "152.118.148.95"
RABBIT_PORT = 5672

MESSAGE_TEMPLATE = "{:d}% compressing file {:s}"

DAEMON_DIR_PATH = '/home/daemon'
PROCESSED_DIR_PATH = DAEMON_DIR_PATH + '/processed'


def execute(routing_key):
    (_, _, filenames) = next(walk(DAEMON_DIR_PATH))
    if len(filenames) > 0:
        for f in filenames:
            campress(f, routing_key)
            move_processed_file(f)


def move_processed_file(filename):
    shutil.move(join(DAEMON_DIR_PATH, filename), join(PROCESSED_DIR_PATH, filename))


def campress(filename, route):
    file = open(join(DAEMON_DIR_PATH, filename), 'rb')
    byte_length = file.seek(0, 2)
    file.seek(0, 0)

    i = 0.1
    while file.tell() < byte_length:
        file.read(1)

        if file.tell() / byte_length >= i:
            msg = MESSAGE_TEMPLATE.format(int(i * 100), filename)
            send_message(msg, route)
            i += 0.1
    send_message(MESSAGE_TEMPLATE.format(int(100), filename), route)
    file.close()


def send_message(message, route):
    time.sleep(0.75)
    cred = pika.PlainCredentials(username=CREDENTIAL_KEY, password=CREDENTIAL_KEY)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT,
                                  virtual_host="/" + CREDENTIAL_KEY, credentials=cred)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=MY_NPM, exchange_type='direct')
    channel.basic_publish(exchange=MY_NPM, routing_key=route, body=message)
    connection.close()
    time.sleep(0.75)
