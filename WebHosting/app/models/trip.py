from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class Trip(BaseModel):
    id: Optional[str] = Field(alias="_id")
    trip_id: int
    devid: int
    lat: float
    lon: float
    speed: float
    tms: int

    def to_dict(self):
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "devid": self.devid,
            "lat": self.lat,
            "lon": self.lon,
            "speed": self.speed,
            "tms": self.tms
        }

    class Config:
        json_encoders = {
            ObjectId: str
        }
        #allow_population_by_field_name = True
        populate_by_name = True
    