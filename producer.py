import json
import random
import signal
import threading
import time

import pika
from decouple import config

from database import fms_drivers_cars

BROKER_HOST = config("BROKER_HOST", default="localhost")
BROKER_QUEUE = config("BROKER_QUEUE", default="queue")
HEARTBEAT_INTERVAL = config("HEARTBEAT_INTERVAL", cast=int)     # seconds


def heartbeat(*args, **kwargs):
    # establish connection to the broker
    connection = pika.BlockingConnection(pika.ConnectionParameters(BROKER_HOST))
    channel = connection.channel()

    # create consumer queue
    channel.queue_declare(queue=BROKER_QUEUE)

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
        channel.basic_publish(exchange="", routing_key=BROKER_QUEUE, body=message)
        print("[x] Published %r" % message)

    # close connection gently
    connection.close()


def signal_handler(*args, **kwargs):
    raise ProgramKilledException


def run():
    # exist program gracefully with a soft kill using signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # create thread for running heartbeat function on interval time in seconds
    thread = Thread(interval=HEARTBEAT_INTERVAL, func=heartbeat)
    thread.start()

    while True:
        try:
            time.sleep(1)
        except ProgramKilledException:
            print("Program killed. Running cleanup code...")
            print("Terminating thread for generating heartbeats...")
            thread.stop()

            print("Bye!")
            break


class Thread(threading.Thread):

    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.event = threading.Event()
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.event.set()
        self.join()

    def run(self):
        while not self.event.wait(self.interval):
            self.func(self.args, self.kwargs)


class ProgramKilledException(Exception):
    pass


if __name__ == "__main__":
    run()

