from typing import Optional

from pydantic import BaseModel


class TripModel(BaseModel):

    name: str
    description: Optional[str] = None

    @classmethod
    def to_json(cls, entity):
        if not entity:
            return dict()

        return dict(id=str(entity["_id"]), name=entity["name"], description=entity["description"])

    class Config:
        schema_extra = {
            "example": {
                "name": "Trip",
                "description": "Trip from location A to B"
            }
        }
