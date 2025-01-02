from app.models.ppdensity import PPDensity
from typing import List
from app.db.postgresql import get_pgdb


# 1420070400000
async def get_ppdensity_ts(timestamp: int) -> List[PPDensity]:
    ppdensities = []
    pgdb_conn = await get_pgdb()
    rows = await pgdb_conn.fetch('select id,longitude,latitude,population_density,timestamp from harbinpp where timestamp=$1', timestamp)
    for row in rows:
        item = PPDensity(
            id=int(row[0]),
            longitude=float(row[1]),
            latitude=float(row[2]),
            population_density=int(row[3]),
            timestamp=int(row[4])
        )
        ppdensities.append(item)
    await pgdb_conn.close()
    return ppdensities

async def get_ppdensity_location(latitude: float, longitude: float) -> List[PPDensity]:
    ppdensities = []
    pgdb_conn = await get_pgdb()
    rows = await pgdb_conn.fetch('select id,longitude,latitude,population_density,timestamp from harbinpp where longitude=$1 and latitude=$2', longitude, latitude)
    for row in rows:
        item = PPDensity(
            id=int(row[0]),
            longitude=float(row[1]),
            latitude=float(row[2]),
            population_density=int(row[3]),
            timestamp=int(row[4])
        )
        ppdensities.append(item)
    await pgdb_conn.close()
    return ppdensities