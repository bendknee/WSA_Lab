import shutil
from os import walk
from os.path import join

import pika

CREDENTIAL_KEY = "0806444524"
MY_NPM = "1606917550"
RABBIT_HOST = "152.118.148.95"
RABBIT_PORT = 5672

DAEMON_DIR_PATH = '/home/daemon'
PROCESSED_DIR_PATH = DAEMON_DIR_PATH + '/processed'
ROUTING_KEY = "X_ROUTING_KEY"


def execute(routing_key):
    (_, _, filenames) = next(walk(DAEMON_DIR_PATH))
    if len(filenames) > 0:
        connection, channel = publisher_setup()
        for f in filenames:
            campress(f, routing_key, channel)
            move_processed_file(f)

        connection.close()


def move_processed_file(filename):
    shutil.move(join(DAEMON_DIR_PATH, filename), join(PROCESSED_DIR_PATH, filename))


def campress(filename, route, channel):
    file = open(join(DAEMON_DIR_PATH, filename), 'rb')
    byte_length = file.seek(0, 2)
    file.seek(0, 0)

    i = 0.1
    while file.tell() < byte_length:
        file.read(1)

        if file.tell() / byte_length >= i:
            send_message(i, filename, route, channel)
            i += 0.1
        # time.sleep(0.0005)
    send_message(1, filename, route, channel)
    file.close()


def publisher_setup():
    cred = pika.PlainCredentials(username=CREDENTIAL_KEY, password=CREDENTIAL_KEY)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT,
                                  virtual_host="/" + CREDENTIAL_KEY, credentials=cred)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=MY_NPM, exchange_type='direct')
    return connection, channel


def send_message(percent, filename, route, channel):
    msg = "{:d}% compressing file {:s}".format(int(percent * 100), filename)
    channel.basic_publish(exchange=MY_NPM, routing_key=route, body=msg)
