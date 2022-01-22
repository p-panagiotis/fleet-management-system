import json
import logging
import random
import sys

import pika
from decouple import config
from pika.exchange_type import ExchangeType

from database.database import fms_drivers_cars

logger = logging.getLogger(__name__)


class Publisher(object):

    EXCHANGE = "fms.exchange"
    EXCHANGE_TYPE = ExchangeType.topic
    QUEUE = "FMS"
    ROUTING_KEY = "FMS.exchange"
    PUBLISH_INTERVAL = config("PUBLISH_INTERVAL", cast=int)

    def __init__(self, amqp_url):
        self._url = amqp_url
        self._connection = None
        self._channel = None

    def connect(self):
        """ Connect to RabbitMQ server """
        logger.info(f"Connecting to {self._url}")
        return pika.SelectConnection(pika.URLParameters(self._url), on_open_callback=self.on_connection_open)

    def on_connection_open(self, *args, **kwargs):
        """ This method is called by pika once the connection to RabbitMQ has been established """
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """ This method is called by pika when the channel has been opened. Declare channel exchange. """
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
            callback=self.on_exchange_declareok
        )

    def on_channel_closed(self):
        self.close_connection()

    def on_exchange_declareok(self, *args, **kwargs):
        """ Invoked by pika when RabbitMQ finished with declaring the exchange. Declare channel queue. """
        self._channel.queue_declare(queue=self.QUEUE, callback=self.on_queue_declareok)

    def on_queue_declareok(self, *args, **kwargs):
        """ Bind the queue and exchange together. """
        self._channel.queue_bind(
            queue=self.QUEUE,
            exchange=self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok
        )

    def on_bindok(self, *args, **kwargs):
        """ Invoked by pika when it receives the bind ok response from RabbitMQ. Schedule next heartbeat. """
        self.schedule_next_heartbeat()

    def schedule_next_heartbeat(self):
        """ Schedule message to be delivered in interval seconds. """
        self._connection.ioloop.call_later(self.PUBLISH_INTERVAL, self.publish_heartbeat)

    def publish_heartbeat(self):
        """ Publish heartbeat to the RabbitMQ server queue. """
        # fetch distinct cars with drivers
        cars = fms_drivers_cars.find({"car_id": {"$ne": None}, "driver_id": {"$ne": None}}).distinct("car_id")

        # process heartbeat for each car
        for car_id in cars:
            # generate random car speed
            speed = random.randint(0, 200)

            # generate geo-coordinates
            lat, long, = (round(random.uniform(34.707130, 35.185566), 6), round(random.uniform(32.429737, 33.636631), 6))
            data = dict(car_id=car_id, speed=speed, latitude=lat, longitude=long)

            # publish message
            message = bytes(json.dumps(data), encoding="utf8")
            self._channel.basic_publish(exchange=self.EXCHANGE, routing_key=self.ROUTING_KEY, body=message)
            logger.info(f"Published heartbeat {message}")

        self.schedule_next_heartbeat()

    def close_channel(self):
        """ Command to close the channel with RabbitMQ server. """
        if self._channel:
            self._channel.close()

    def close_connection(self):
        """ Command to close the connection with RabbitMQ server. """
        if self._connection:
            self._connection.close()

    def stop(self):
        """ Terminate connection and channel with RabbitMQ server. """
        self.close_channel()
        self.close_connection()

    def run(self):
        """ Run publisher by connecting and starting the IOLoop. """
        try:
            self._connection = self.connect()
            self._connection.ioloop.start()
        except KeyboardInterrupt:
            self.stop()
            self._connection.ioloop.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    publisher = Publisher(amqp_url=config("AMQP_URL"))
    publisher.run()
