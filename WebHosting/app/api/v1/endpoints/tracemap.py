from fastapi import APIRouter, Query
from typing import List,Optional
import app.services.tracemap_service  as TracemapService


router = APIRouter()

@router.get("/tracemap")
async def get_tracemap():
    return await TracemapService.renderhtml()


