from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from database.database import fms_cars
from app.models.car import CarModel

router = APIRouter()


@router.post("/")
def add_car(car: CarModel):
    # convert car model data to json
    data = jsonable_encoder(car)
    # insert car to db
    entity = fms_cars.insert_one(data)
    # get new car from db
    new_entity = fms_cars.find_one({"_id": entity.inserted_id})

    return CarModel.to_json(new_entity)


@router.get("/")
def get_all_cars():
    # get all cars from the database
    entities = fms_cars.find()

    # process entities to json
    data = [CarModel.to_json(entity) for entity in entities]
    return data


@router.get("/{id}")
def get_car(id: str):
    try:
        # get car with given id
        entity = fms_cars.find_one({"_id": ObjectId(id)})
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with ID '{id}' does not exist")

    return CarModel.to_json(entity)


@router.put("/{id}")
def update_car(id: str, car: CarModel):
    # convert car model data to json
    data = jsonable_encoder(car)

    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # check if car exists with given id
    entity = fms_cars.find_one({"_id": entity_id})
    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with ID '{id}' does not exist")

    # update all car properties
    updated_car = fms_cars.update_one({"_id": entity_id}, {"$set": data})
    if updated_car:
        return {"message": f"Car with ID '{id}' updated successfully"}

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"An error occurred. There was an error updating the car with ID '{id}'"
    )


@router.delete("/{id}")
def delete_car(id: str):
    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # check car if exists before deletion
    entity = fms_cars.find_one({"_id": entity_id})

    # in case car does not exist then we do nothing
    if not entity:
        return None

    # delete car from database
    deleted_car = fms_cars.delete_one({"_id": entity_id})
    if deleted_car:
        return {"message": f"Car with ID '{id}' deleted successfully"}

    return None
