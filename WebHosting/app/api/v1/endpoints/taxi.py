from fastapi import FastAPI
from app.services.taxi_service import get_nearby_drivers, find_nearest_driver, get_route, haversine, Location, data_to_geodf
from fastapi import APIRouter

router = APIRouter()

@router.post("/taxi_app")
def dispatch_taxi(location: Location):
    gdf = data_to_geodf()
    drivers = get_nearby_drivers(gdf, location.latitude, location.longitude)
    if drivers.empty:
        return {"message": "附近没有司机"}
    
    nearest_driver = find_nearest_driver(location.latitude, location.longitude, drivers)
    if not nearest_driver.empty:
        driver_lat = nearest_driver['lat']
        driver_lon = nearest_driver['lon']
        route = get_route(start_lat=driver_lat, start_lon=driver_lon, end_lat=location.latitude, end_lon=location.longitude)
        return {
            "message": f"派单给司机: {nearest_driver['devid']}, 距离您{round(haversine(location.longitude, location.latitude, driver_lon, driver_lat), 2)}千米",
            "route": route,
            "driver_lat": driver_lat,
            "driver_lon": driver_lon
        }
    else:
        return {"message": "没有找到合适的司机"}
    