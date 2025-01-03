from fastapi import APIRouter
import app.services.top10area_service as Top10AreaService

router = APIRouter()

@router.get("/top-ten-locations")
async def get_top_ten_locations():
    return await Top10AreaService.get_top_ten_locations()


@router.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
