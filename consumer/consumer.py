import json
import logging
import sys

import pika
from decouple import config
from pika.exchange_type import ExchangeType

from database import fms_drivers_cars, fms_drivers_penalties

logger = logging.getLogger(__name__)


class Consumer(object):

    EXCHANGE = "fms.exchange"
    EXCHANGE_TYPE = ExchangeType.topic
    QUEUE = "FMS"
    ROUTING_KEY = "FMS.exchange"

    def __init__(self, amqp_url):
        self._url = amqp_url
        self._connection = None
        self._channel = None
        self._consumer_tag = None

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
        """ Invoked by pika when RabbitMQ closes the channel. """
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
        self.set_channel_qos()

    def set_channel_qos(self):
        """ Sets up the consumer prefetch to only be delivered one message at a time """
        self._channel.basic_qos(prefetch_count=1, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, *args, **kwargs):
        """ Invoked by pika when the basic qos method has completed. Start consuming messages from queue """
        self.start_consuming()

    def start_consuming(self):
        """ Starts basic queue consuming from RabbitMQ server. """
        self._consumer_tag = self._channel.basic_consume(
            queue=self.QUEUE,
            auto_ack=True,
            on_message_callback=self.consume_heartbeat
        )

    def stop_consuming(self):
        """ Terminate queue consumer with RabbitMQ server. """
        if self._channel:
            self._channel.basic_cancel(self._consumer_tag, callback=self.close_channel)

    def consume_heartbeat(self, channel, method, properties, body):
        logger.info(f"Received heartbeat {body}")
        data = json.loads(body)

        car_id = data["car_id"]
        speed = int(data["speed"])
        latitude = data["latitude"]
        longitude = data["longitude"]

        # find driver
        entity = fms_drivers_cars.find_one({"car_id": car_id})
        driver_id = str(entity["driver_id"])

        # calculate penalty points if any
        penalty_points = 0

        if 60 < speed <= 80:
            penalty_points = 80 - speed
        elif 80 < speed <= 100:
            penalty_points = (100 - speed) * 2
        elif speed > 100:
            penalty_points = (speed - 100) * 5

        if penalty_points > 0:
            # store penalty points if any
            fms_drivers_penalties.insert_one({
                "driver_id": driver_id,
                "speed": speed,
                "penalty_points": penalty_points,
                "latitude": latitude,
                "longitude": longitude
            })

    def close_channel(self):
        """ Command to close the channel with RabbitMQ server. """
        if self._channel:
            self._channel.close()

    def close_connection(self):
        """ Command to close the connection with RabbitMQ server. """
        if self._connection:
            self._connection.close()

    def stop(self):
        """ Terminate connection with RabbitMQ server. """
        self.stop_consuming()

    def run(self):
        """ Run consumer by connecting and starting the IOLoop. """
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

    consumer = Consumer(amqp_url=config("AMQP_URL"))
    consumer.run()
