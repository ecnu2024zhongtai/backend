from fastapi import APIRouter, Query
from app.models.demand import Demand
from typing import List,Optional
import app.services.demand_service  as DemandService
import app.services.demand_forecast_service as ForecastService

router = APIRouter()

@router.get("/demands", response_model= List[Demand])
async def get_demands(dayid: int,
                      lon_index: Optional[int] = Query(None),
                      lat_index: Optional[int] = Query(None),
                      time_index: Optional[int] = Query(None)):
    return await DemandService.get_demands(dayid, lon_index, lat_index, time_index)

@router.get("/demands/last10mins", response_model= List[Demand])
async def get_last_10mins_demands_from_redis():
    return await DemandService.get_recent_10mins_demands_from_redis()


@router.get("/demands/last10mins/loadtoredis")
async def get_demands():
    return await DemandService.load_last_10mins_Demand_to_redis()

@router.get("/demands/forecast")
async def forecast_demand():
    return await ForecastService.forecast_demand()