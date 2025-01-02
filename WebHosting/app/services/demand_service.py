from app.models.demand import Demand
from typing import List,Optional
from app.db.postgresql import get_pgdb


# 4,5,6,7
async def get_demands(dayid: int,
                             lon_index: Optional[int] = None, 
                             lat_index: Optional[int] = None, 
                             time_index: Optional[int] = None) -> List[Demand]:
    demands = []
    pgdb_conn = await get_pgdb()
    query = 'select dayid,lon_index,lat_index,time_index,ppdensity,trip_count from forecast_dataset where dayid=$1'

    params = [dayid]

    if lon_index is not None:
        query += ' AND lon_index=$2'
        params.append(lon_index)
    
    if lat_index is not None:
        query += ' AND lat_index=$3'
        params.append(lat_index)
    
    if time_index is not None:
        query += ' AND time_index=$4'
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