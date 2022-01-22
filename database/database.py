import pymongo
from decouple import config

# get connection string from .env file
MONGO_CONNECTION_STRING = config("MONGO_CONNECTION_STRING")
# initialize database connection
client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
# create database
db = client.fms

# get database collections
fms_drivers = db.get_collection("fms_drivers")
fms_drivers_cars = db.get_collection("fms_drivers_cars")
fms_drivers_penalties = db.get_collection("fms_drivers_penalties")
fms_cars = db.get_collection("fms_cars")
fms_trips = db.get_collection("fms_trips")
