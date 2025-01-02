from fastapi import APIRouter, Query
from app.models.demand import Demand
from typing import List,Optional
import app.services.demand_service  as DemandService


router = APIRouter()

@router.get("/demands", response_model= List[Demand])
async def get_demands(dayid: int,
                      lon_index: Optional[int] = Query(None),
                      lat_index: Optional[int] = Query(None),
                      time_index: Optional[int] = Query(None)):
    return await DemandService.get_demands(dayid, lon_index, lat_index, time_index)


