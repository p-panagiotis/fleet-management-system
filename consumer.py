import json
import sys

import pika
from decouple import config

from database import fms_drivers_cars, fms_drivers_penalties

BROKER_HOST = config("BROKER_HOST", default="localhost")
BROKER_QUEUE = config("BROKER_QUEUE", default="queue")


def run():
    # establish connection to the broker
    connection = pika.BlockingConnection(pika.ConnectionParameters(BROKER_HOST))
    channel = connection.channel()

    # create consumer queue
    channel.queue_declare(queue=BROKER_QUEUE)

    # consume messages from queue
    channel.basic_consume(queue=BROKER_QUEUE, auto_ack=True, on_message_callback=consume)

    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


def consume(channel, method, properties, body):
    print("[x] Received %r" % body)
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


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
