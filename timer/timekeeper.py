from datetime import datetime

from utils.broker import BrokerUtils, MODE_TOPIC, CHANNEL_TIMER


def play_time():
    broker = BrokerUtils(MODE_TOPIC)
    while True:
        the_time_is_now = datetime.now().strftime("%H:%M:%S %d %B %Y")
        broker.send(the_time_is_now, CHANNEL_TIMER)
