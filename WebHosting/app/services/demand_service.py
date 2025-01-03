from app.models.demand import Demand
from typing import List,Optional
from app.db.postgresql import get_pgdb
from datetime import datetime, timezone
from app.schemas.RedisKey import RedisKey
from app.db.redis_connection import get_redis
import json


# 4,5,6,7
async def get_demands(dayid: int,
                             lon_index: Optional[int] = None, 
                             lat_index: Optional[int] = None, 
                             time_index: Optional[int] = None) -> List[Demand]:
    demands = []
    pgdb_conn = await get_pgdb()
    query = 'select dayid,lon_index,lat_index,time_index,ppdensity,trip_count from forecast_dataset where dayid=$1'
    parsmcount = 2
    params = [dayid]

    if lon_index is not None:
        query += ' AND lon_index=$' + str(parsmcount)
        params.append(lon_index)
        parsmcount += 1
    
    if lat_index is not None:
        query += ' AND lat_index=$' + str(parsmcount)
        params.append(lat_index)
        parsmcount += 1
    
    if time_index is not None:
        query += ' AND time_index=$'+ str(parsmcount)
        params.append(time_index)

    rows = await pgdb_conn.fetch(query, *params)
    for row in rows:
        item = Demand(
            dayid=int(row[0]),
            lon_index=int(row[1]),
            lat_index=int(row[2]),
            time_index=int(row[3]),
            ppdensity=int(row[4]),
            trip_count=int(row[5])
        )
        demands.append(item)
    await pgdb_conn.close()
    return demands

async def load_last_10mins_Demand_to_redis():
    current_time_index = get_current_time_index()
    demands = await get_demands(dayid=7, time_index=current_time_index)
    demands_dict_list = [demand.to_dict() for demand in demands]  # 将 Trip 对象列表转换为字典列表
    redis = await get_redis()
    await redis.set(RedisKey.recent_10mins_demand_key(), json.dumps(demands_dict_list))
    await redis.close()
    return {"status": "success", "message": "10 mins demands loaded to Redis"}

async def get_recent_10mins_demands_from_redis():
    redis = await get_redis()
    demands_str = await redis.get(RedisKey.recent_10mins_demand_key())
    await redis.close()
    if demands_str is None:
        return []
    try:
        demands_list = json.loads(demands_str)  # 将 JSON 字符串反序列化为列表
        demands = [Demand(**demand) for demand in demands_list]  # 将字典列表转换为 Trip 对象列表
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode JSON"}
    return demands


def get_current_time_index():
    time_index = get_today_seconds() // 600
    return time_index

def get_today_seconds():
    # Get the current UTC time
    current_time = datetime.now(timezone.utc)

    # Get the start of the current day (00:00:00 UTC)
    start_of_day = datetime(current_time.year, current_time.month, current_time.day, tzinfo=timezone.utc)

    # Calculate the number of seconds since the start of the day
    seconds_since_start_of_day = int((current_time - start_of_day).total_seconds())

    return seconds_since_start_of_day