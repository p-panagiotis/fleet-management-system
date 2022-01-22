from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from database.database import fms_trips
from app.models.trip import TripModel

router = APIRouter()


@router.post("/")
def add_trip(trip: TripModel):
    # convert trip model data to json
    data = jsonable_encoder(trip)
    # insert trip to db
    entity = fms_trips.insert_one(data)
    # get new trip from db
    new_entity = fms_trips.find_one({"_id": entity.inserted_id})

    return TripModel.to_json(new_entity)


@router.get("/")
def get_all_trips():
    # get all trips from the database
    entities = fms_trips.find()

    # process entities to json
    data = [TripModel.to_json(entity) for entity in entities]
    return data


@router.get("/{id}")
def get_trip(id: str):
    try:
        # get trip with given id
        entity = fms_trips.find_one({"_id": ObjectId(id)})
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with ID '{id}' does not exist")

    return TripModel.to_json(entity)


@router.put("/{id}")
def update_trip(id: str, trip: TripModel):
    # convert car model data to json
    data = jsonable_encoder(trip)

    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    entity = fms_trips.find_one({"_id": entity_id})
    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with ID '{id}' does not exist")

    # update all trip properties
    updated_trip = fms_trips.update_one({"_id": entity_id}, {"$set": data})
    if updated_trip:
        return {"message": f"Trip with ID '{id}' updated successfully"}

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"An error occurred. There was an error updating the trip with ID '{id}'"
    )


@router.delete("/{id}")
def delete_trip(id: str):
    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # check trip if exists before deletion
    entity = fms_trips.find_one({"_id": entity_id})

    # in case car does not exist then we do nothing
    if not entity:
        return None

    # delete car from database
    deleted_trip = fms_trips.delete_one({"_id": entity_id})
    if deleted_trip:
        return {"message": f"Trip with ID {id} deleted successfully"}

    return None
