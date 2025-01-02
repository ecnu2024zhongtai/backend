from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import config
from taxi import get_nearby_drivers, find_nearest_driver, get_route, haversine, Location, data_to_geodf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/taxi_app")
def dispatch_taxi(location: Location):
    gdf = data_to_geodf()
    drivers = get_nearby_drivers(gdf, location.latitude, location.longitude)
    if drivers.empty:
        return {"message": "附近没有司机"}
    
    nearest_driver = find_nearest_driver(location.latitude, location.longitude, drivers)
    if not nearest_driver.empty:
        driver_lat = nearest_driver['lat']
        driver_lon = nearest_driver['lon']
        route = get_route(location.latitude, location.longitude, driver_lat, driver_lon)
        return {
            "message": f"派单给司机: {nearest_driver['devid']}, 距离您{round(haversine(location.longitude, location.latitude, driver_lon, driver_lat), 2)}千米",
            "route": route,
            "driver_lat": driver_lat,
            "driver_lon": driver_lon
        }
    else:
        return {"message": "没有找到合适的司机"}
    

@app.get("/taxi", response_class=HTMLResponse)
async def get_map():
    map_file = config.TAXI_SAVE_PATH

    with open(map_file, "r", encoding="utf-8") as f:
        map_html = f.read()

    return HTMLResponse(content=map_html)


if __name__ == '__main__':
    location = Location(latitude=45.803775, longitude=126.534967)  # 测试
    dispatch_taxi(location)