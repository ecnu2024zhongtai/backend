from pydantic import BaseModel
from typing import Optional

class TripCreate(BaseModel):
    trip_id: int
    devid: int
    lat: float
    lon: float
    speed: float
    tms: int

    class Config:
        #allow_population_by_field_name = True
        populate_by_name = True

class GetTripsByTimeRequest(BaseModel):
    start_timestamp: int
    end_timestamp: int
    limit: int
    devid: Optional[int] = None
    trip_id: Optional[int] = None
    
    class Config:
        #allow_population_by_field_name = True
        populate_by_name = True