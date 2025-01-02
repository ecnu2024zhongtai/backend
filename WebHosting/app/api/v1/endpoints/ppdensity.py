from fastapi import APIRouter
from app.models.ppdensity import PPDensity
from typing import List
import app.services.ppdensity_service  as PPDensityService


router = APIRouter()

## 1420070400000
@router.get("/ppdensity/ts", response_model= List[PPDensity])
async def get_ppdensity_ts_endpoint(timestamp: int):
    return await PPDensityService.get_ppdensity_ts(timestamp)

@router.get("/ppdensity/location", response_model= List[PPDensity])
async def get_ppdensity_location_endpoint(latitude: float, longitude: float):
    return await PPDensityService.get_ppdensity_location(latitude, longitude)

###
# 45.40416666666613  45.41249999999946  0.008333333 45.4 
# 46.09583333333279  46.08749999999946  0.008333333 46.1
# 127.05416666666545 127.04583333333213 0.008333333 127.058333333
# 126.0874999999988  126.09583333333212 0.008333333 126.083333333
###

# (45.40416666666613 - 45.4)/0.008333333
# (46.09583333333279 - 45.40416666666613) / 0.008333333 = 83
# (127.05416666666545 - 126.0874999999988) / 0.008333333 = 116