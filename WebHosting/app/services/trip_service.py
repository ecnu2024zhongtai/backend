from pymongo.collection import Collection
from app.models.trip import Trip
from app.schemas.trip import TripCreate
from app.db.mongodb import trip_collection
from typing import List, Optional
from datetime import datetime, timezone
from app.schemas.RedisKey import RedisKey
from app.db.redis_connection import get_redis
from aioredis import Redis
from fastapi import Depends
import json
import ast


async def create_trip(trip: TripCreate):
    trip_dict = trip.dict()
    result = trip_collection.insert_one(trip_dict)
    return Trip(**trip_dict, id=str(result.inserted_id))

async def get_trips() -> List[Trip]:
    trips = []
    async for trip in trip_collection.find():
        trips.append(Trip(**trip, id=str(trip["_id"])))
    return trips

async def get_trips_tt(start_timestamp: int, end_timestamp: int, limit: Optional[int] = None, devid: Optional[int] = None, trip_id: Optional[int] = None) -> List[Trip]:
    trips = []
    query = {"tms": {"$gte": start_timestamp, "$lte": end_timestamp}}
    
    if devid is not None:
        query["devid"] = devid
    if trip_id is not None:
        query["trip_id"] = trip_id

    cursor = trip_collection.find(query).sort("tms", -1)
    if limit is not None:
        cursor = cursor.limit(limit)

    async for trip in cursor:
        trip_data = {**trip, "_id": str(trip["_id"])}
        trips.append(Trip(**trip_data))
    return trips


async def load_last_2mins_to_redis():
    to_timestamp = 1420588800 + get_today_seconds()
    from_timestamp = to_timestamp - 120
    trips = await get_trips_tt(start_timestamp=from_timestamp, end_timestamp=to_timestamp)
    trips_dict_list = [trip.to_dict() for trip in trips]  # 将 Trip 对象列表转换为字典列表
    redis = await get_redis()
    await redis.set(RedisKey.recent_2mins_trip_key(), json.dumps(trips_dict_list))
    await redis.close()
    return {"status": "success", "message": "Trips loaded to Redis"}

async def load_last_5mins_to_redis():
    to_timestamp = 1420588800 + get_today_seconds()
    from_timestamp = to_timestamp - 60*5
    trips = await get_trips_tt(start_timestamp=from_timestamp, end_timestamp=to_timestamp)
    trips_dict_list = [trip.to_dict() for trip in trips]  # 将 Trip 对象列表转换为字典列表
    redis = await get_redis()
    await redis.set(RedisKey.recent_5mins_trip_key(), json.dumps(trips_dict_list))
    await redis.close()
    return {"status": "success", "message": "Trips loaded to Redis"}

async def load_last_10mins_to_redis():
    to_timestamp = 1420588800 + get_today_seconds()
    from_timestamp = to_timestamp - 60*10
    trips = await get_trips_tt(start_timestamp=from_timestamp, end_timestamp=to_timestamp)
    trips_dict_list = [trip.to_dict() for trip in trips]  # 将 Trip 对象列表转换为字典列表
    redis = await get_redis()
    await redis.set(RedisKey.recent_10mins_trip_key(), json.dumps(trips_dict_list))
    await redis.close()
    return {"status": "success", "message": "Trips loaded to Redis"}

async def load_last_1hour_to_redis():
    to_timestamp = 1420588800 + get_today_seconds()
    from_timestamp = to_timestamp - 3600
    trips = await get_trips_tt(start_timestamp=from_timestamp, end_timestamp=to_timestamp)
    trips_dict_list = [trip.to_dict() for trip in trips]  # 将 Trip 对象列表转换为字典列表
    redis = await get_redis()
    await redis.set(RedisKey.recent_1hour_trip_key(), json.dumps(trips_dict_list))
    await redis.close()
    return {"status": "success", "message": "1 hour Trips loaded to Redis"}

async def get_recent_5mins_trips_from_redis():
    redis = await get_redis()
    trips_str = await redis.get(RedisKey.recent_5mins_trip_key())
    await redis.close()
    if trips_str is None:
        return []
    try:
        trips_list = json.loads(trips_str)  # 将 JSON 字符串反序列化为列表
        trips = [Trip(**trip) for trip in trips_list]  # 将字典列表转换为 Trip 对象列表
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode JSON"}
    return trips

async def get_recent_10mins_trips_from_redis():
    redis = await get_redis()
    trips_str = await redis.get(RedisKey.recent_10mins_trip_key())
    await redis.close()
    if trips_str is None:
        return []
    try:
        trips_list = json.loads(trips_str)  # 将 JSON 字符串反序列化为列表
        trips = [Trip(**trip) for trip in trips_list]  # 将字典列表转换为 Trip 对象列表
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode JSON"}
    return trips

async def get_recent_1hour_trips_from_redis():
    redis = await get_redis()
    trips_str = await redis.get(RedisKey.recent_1hour_trip_key())
    await redis.close()
    if trips_str is None:
        return []
    try:
        trips_list = json.loads(trips_str)  # 将 JSON 字符串反序列化为列表
        trips = [Trip(**trip) for trip in trips_list]  # 将字典列表转换为 Trip 对象列表
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode JSON"}
    return trips


async def get_recent_trips_from_redis():
    redis = await get_redis()
    trips_str = await redis.get(RedisKey.recent_2mins_trip_key())
    await redis.close()
    if trips_str is None:
        return []
    try:
        trips_list = json.loads(trips_str)  # 将 JSON 字符串反序列化为列表
        trips = [Trip(**trip) for trip in trips_list]  # 将字典列表转换为 Trip 对象列表
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode JSON"}
    return trips

def get_today_seconds():
    # Get the current UTC time
    current_time = datetime.now(timezone.utc)

    # Get the start of the current day (00:00:00 UTC)
    start_of_day = datetime(current_time.year, current_time.month, current_time.day, tzinfo=timezone.utc)

    # Calculate the number of seconds since the start of the day
    seconds_since_start_of_day = int((current_time - start_of_day).total_seconds())

    return seconds_since_start_of_day

