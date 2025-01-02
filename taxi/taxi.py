from fastapi import FastAPI
from pydantic import BaseModel
import requests
import math
import geopandas as gpd
from shapely.geometry import Point
import config

app = FastAPI()

# 高德地图API Key
API_KEY = config.API_KEY
data_url = config.DRIVER_DATA_URL


class Location(BaseModel):
    latitude: float = 45.803775
    longitude: float = 126.534967


# 计算两个经纬度之间的距离
def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # 地球半径，单位为公里
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def data_to_geodf():
    response = requests.get(data_url)
    data = response.json()
    gdf = gpd.GeoDataFrame(data)
    gdf['geometry'] = gdf.apply(lambda row: Point(row["lon"], row["lat"]), axis=1)
    gdf = gdf.set_geometry('geometry')
    return gdf


# 获取附近的司机位置
def get_nearby_drivers(gbf, latitude, longitude, radius=10):
    spatial_index = gbf.sindex
    point = Point(longitude, latitude)
    buffer = point.buffer(radius / 111.32)  # 1度约等于111.32公里
    possible_match_index = list(spatial_index.intersection(buffer.bounds))
    possible_match = gbf.iloc[possible_match_index]
    precise_match = possible_match[possible_match.intersects(buffer)]

    return precise_match


# 选取最近的司机
def find_nearest_driver(latitude, longitude, drivers):
    min_distance = float('inf')
    nearest_driver = None
    for _, driver in drivers.iterrows():
        driver_lat = float(driver["lat"])
        driver_lon = float(driver["lon"])
        distance = haversine(longitude, latitude, driver_lon, driver_lat)
        if distance < min_distance:
            min_distance = distance
            nearest_driver = driver
    return nearest_driver


def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f'https://restapi.amap.com/v3/direction/driving?key={API_KEY}&origin={start_lon},{start_lat}&destination={end_lon},{end_lat}'
    response = requests.get(url)
    return response.json()
