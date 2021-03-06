from datetime import date

from pydantic import BaseModel


class DriverModel(BaseModel):

    first_name: str
    last_name: str
    age: int
    gender: str
    license_date: date

    @classmethod
    def to_json(cls, entity):
        if not entity:
            return dict()

        return dict(
            id=str(entity["_id"]),
            first_name=entity["first_name"],
            last_name=entity["last_name"],
            age=entity["age"],
            gender=entity["gender"],
            license_date=entity["license_date"]
        )

    class Config:
        schema_extra = {
            "example": {
                "first_name": "FMS User",
                "last_name": "FMS User",
                "age": 31,
                "gender": "Male",
                "license_date": "2022-01-20"
            }
        }


class DriverCarModel(BaseModel):

    driver_id: str
    car_id: str

    @classmethod
    def to_json(cls, entity):
        if not entity:
            return dict()

        return dict(id=str(entity["_id"]), name=entity["driver_id"], description=entity["car_id"])

    class Config:
        schema_extra = {
            "example": {
                "driver_id": "61e9d7fa22d8e7b0e053d289",
                "car_id": "61e9d158a2353cb8b98217ca"
            }
        }


class DriverPenaltyModel(BaseModel):

    driver_id: str
    penalty: str

    @classmethod
    def to_json(cls, entity):
        if not entity:
            return dict()

        return dict(
            id=str(entity["_id"]),
            name=entity["driver_id"],
            speed=entity["speed"],
            penalty_points=entity["penalty_points"],
            latitude=entity["latitude"],
            longitude=entity["longitude"]
        )

    class Config:
        schema_extra = {
            "example": {
                "driver_id": "61e9d7fa22d8e7b0e053d289",
                "speed": 81,
                "penalty_points": 2,
                "latitude": "34.749168",
                "longitude": "32.569975"
            }
        }
