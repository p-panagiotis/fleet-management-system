from pydantic import BaseModel


class CarModel(BaseModel):

    brand: str

    @classmethod
    def to_json(cls, entity):
        if not entity:
            return dict()

        return dict(id=str(entity["_id"]), brand=entity["brand"])

    class Config:
        schema_extra = {
            "example": {
                "brand": "Mazda"
            }
        }
