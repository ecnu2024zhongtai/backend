from pydantic import BaseModel

class Demand(BaseModel):
    dayid: int
    lat_index: int
    lon_index: int
    time_index: int
    ppdensity: int
    trip_count: int

    def to_dict(self):
        return {
            "dayid": self.dayid,
            "lat_index": self.lat_index,
            "lon_index": self.lon_index,
            "time_index": self.time_index,
            "ppdensity": self.ppdensity,
            "trip_count": self.trip_count
        }
    
    class Config:
        populate_by_name = True