from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from database import fms_drivers, fms_drivers_cars, fms_cars, fms_drivers_penalties
from models import DriverModel, DriverCarModel, DriverPenaltyModel

router = APIRouter()


@router.post("/")
def add_driver(driver: DriverModel):
    # convert driver model data to json
    data = jsonable_encoder(driver)
    # insert driver to db
    entity = fms_drivers.insert_one(data)
    # get new driver from db
    new_entity = fms_drivers.find_one({"_id": entity.inserted_id})

    return DriverModel.to_json(new_entity)


@router.get("/")
def get_all_drivers():
    # get all drivers from the database
    entities = fms_drivers.find()

    # process entities to json
    data = [DriverModel.to_json(entity) for entity in entities]
    return data


@router.get("/{id}")
def get_driver(id: str):
    try:
        # get driver with given id
        entity = fms_drivers.find_one({"_id": ObjectId(id)})
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID '{id}' does not exist")

    return DriverModel.to_json(entity)


@router.put("/{id}")
def update_driver(id: str, driver: DriverModel):
    # convert driver model data to json
    data = jsonable_encoder(driver)

    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # check if driver exists with given id
    entity = fms_drivers.find_one({"_id": entity_id})
    if not entity:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID '{id}' does not exist")

    # update all driver properties
    updated_driver = fms_drivers.update_one({"_id": entity_id}, {"$set": data})
    if updated_driver:
        return {"message": f"Driver with ID '{id}' updated successfully"}

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"An error occurred. There was an error updating the driver with ID '{id}'"
    )


@router.delete("/{id}")
def delete_driver(id: str):
    try:
        # translate given id as ObjectId
        entity_id = ObjectId(id)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # check driver if exists before deletion
    entity = fms_drivers.find_one({"_id": entity_id})

    # in case driver does not exist then we do nothing
    if not entity:
        return None

    # delete driver from database
    deleted_driver = fms_drivers.delete_one({"_id": entity_id})
    if deleted_driver:
        return {"message": f"Driver with ID '{id}' deleted successfully"}

    return None


@router.post("/{driver_id}/car/{car_id}")
def assign_driver_to_car(driver_id: str, car_id: str):
    try:
        # get driver with given id
        driver = fms_drivers.find_one({"_id": ObjectId(driver_id)})
        if not driver:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver with ID '{driver_id}' does not exist"
            )

        # get car with given id
        car = fms_cars.find_one({"_id": ObjectId(car_id)})
        if not car:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Car with ID '{car_id}' does not exist")

        # check if driver already assigned a car
        driver_car = fms_drivers_cars.find_one({"driver_id": driver_id, "car_id": {"$ne": None}})
        if driver_car:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver with ID '{driver_id}' already assigned to a car"
            )

        # in case driver does not have a car assign the requested pair
        entity = fms_drivers_cars.insert_one({"driver_id": driver_id, "car_id": car_id})
        # get new driver car entity
        new_entity = fms_drivers_cars.find_one({"_id": entity.inserted_id})
        return DriverCarModel.to_json(new_entity)
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{driver_id}/penalties")
def get_driver_penalties(driver_id: str):
    try:
        # get driver with given id
        driver = fms_drivers.find_one({"_id": ObjectId(driver_id)})
        if not driver:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver with ID '{driver_id}' does not exist"
            )

        # get all driver penalties
        entities = fms_drivers_penalties.find({"driver_id": driver_id})

        # process entities to json
        data = []
        for entity in entities:
            entity_json = DriverPenaltyModel.to_json(entity)
            data.append(entity_json)

        return data
    except InvalidId as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
