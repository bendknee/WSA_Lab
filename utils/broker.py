import pika

CHANNEL_COMPRESS = "queue.compress.{:s}"
CHANNEL_DOWNLOAD = "queue.download"
CHANNEL_PROGRESS = "queue.progress.{:s}"
CHANNEL_TIMER = "queue.timer"

MODE_DIRECT = 'DIRECT'
MODE_TOPIC = 'TOPIC'


class BrokerUtils:
    _credential_key = "0806444524"
    _npm = "1606917550"
    _rabbit_host = "152.118.148.95"
    _rabbit_port = 5672

    def __init__(self, exchange_type):
        cred = pika.PlainCredentials(username=self._credential_key, password=self._credential_key)
        self.param = pika.ConnectionParameters(host=self._rabbit_host, port=self._rabbit_port,
                                               virtual_host="/" + self._credential_key, credentials=cred)

        if exchange_type in [MODE_DIRECT, MODE_TOPIC]:
            self.exchange_name = "{:s}_{:s}".format(self._npm, exchange_type)
            self.exchange_type = exchange_type.lower()
        else:
            raise RuntimeError("{:s} is an invalid exchange type".format(exchange_type))

    def send(self, message, routing_key):
        connection = pika.BlockingConnection(parameters=self.param)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)
        channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key, body=message)
        connection.close()

    def receive(self, routing_key, handler):
        connection = pika.BlockingConnection(parameters=self.param)
        channel = connection.channel()

        channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)
        result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=routing_key)

        channel.basic_consume(queue=queue_name, on_message_callback=handler, auto_ack=True)
        channel.start_consuming()
