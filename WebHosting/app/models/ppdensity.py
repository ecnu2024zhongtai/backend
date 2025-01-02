from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class PPDensity(BaseModel):
    id: int
    latitude: float
    longitude: float
    population_density: int
    timestamp: int

    def to_dict(self):
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "population_density": self.population_density,
            "timestamp": self.timestamp
        }
    
    class Config:
        populate_by_name = True