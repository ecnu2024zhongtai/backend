from fastapi import APIRouter
from app.schemas.trip import TripCreate
from app.schemas.trip import GetTripsByTimeRequest
from app.models.trip import Trip
from typing import List
from app.services.trip_service import create_trip, get_trips, get_trips_tt
import app.services.trip_service as TripService


router = APIRouter()

@router.post("/trips/", response_model=TripCreate)
async def create_trip_endpoint(trip: TripCreate):
    return await create_trip(trip)


@router.get("/trips/", response_model=List[Trip])
async def get_trips_endpoint():
    return await get_trips()

@router.post("/trips/getbytime", response_model= List[Trip])
async def get_trips_bytime_endpoint(request: GetTripsByTimeRequest):
    return await get_trips_tt(
        request.start_timestamp,
        request.end_timestamp,
        request.limit,
        request.devid,
        request.trip_id
    )

## Load last 2 mins origin trips to redis
## for scheduled job
@router.get("/trips/loadtoredis")
async def load_last_2mins_to_redis():
    return await TripService.load_last_2mins_to_redis()

## Load recent origin trips from redis
@router.get("/trips/recent", response_model= List[Trip])
async def get_recent_trips_from_redis():
    return await TripService.get_recent_trips_from_redis()


## Load last 1 hour origin trips to redis
## for scheduled job
@router.get("/trips/load1hourtoredis")
async def load_last_1hour_to_redis():
    return await TripService.load_last_1hour_to_redis()

## Load recent origin trips from redis
@router.get("/trips/recent/1hour", response_model= List[Trip])
async def get_recent_1hour_trips_from_redis():
    return await TripService.get_recent_1hour_trips_from_redis()