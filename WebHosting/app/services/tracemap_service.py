import app.services.trip_service as TripService
from datetime import datetime
import pandas as pd
import geopandas as gpd
import transbigdata as tbd
import uuid
import os
from keplergl import KeplerGl
from fastapi.responses import HTMLResponse

async def loaddata():
    records = await TripService.get_recent_10mins_trips_from_redis()

    results = []
    for record in records:
        try:
            devid = record.devid
            speed = record.speed
            lat = record.lat
            lon = record.lon
            tms = record.tms
            if all([devid, speed, lat, lon, tms]):
                time_str = datetime.fromtimestamp(tms).strftime("%Y-%m-%d %H:%M:%S")
                results.append({
                    "devid": devid,
                    "speed": speed,
                    "latitude": lat,
                    "longitude": lon,
                    "time_str": time_str
                })
        except Exception as e:
            print(f"Error processing record: {record}, {e}")
    return results


async def transferdata():
    try:
        results = await loaddata()
        dfdata = pd.DataFrame(results, columns=['devid', 'speed', 'latitude', 'longitude', 'time_str'])
        dfdata['longitude'] = pd.to_numeric(dfdata['longitude'], errors='coerce')
        dfdata['speed'] = pd.to_numeric(dfdata['speed'], errors='coerce')
        dfdata['latitude'] = pd.to_numeric(dfdata['latitude'], errors='coerce')
        dfdata['devid'] = pd.to_numeric(dfdata['devid'], downcast='integer', errors='coerce')
        if 'OpenStatus' not in dfdata.columns:
            dfdata['OpenStatus'] = 0  # 默认值为 0

        dfdata.reset_index(drop=True, inplace=True)

        hrb = gpd.read_file('realmap.json')
        if hrb.crs is None:
            hrb.set_crs("EPSG:4326", inplace=True)

        dfdata = tbd.clean_outofshape(dfdata, hrb, col=['longitude', 'latitude'], accuracy=500)
        dfdata = tbd.clean_taxi_status(dfdata, col=['devid', 'time_str', 'OpenStatus'])
        return dfdata
    except Exception as e:
        print(f"Error in transferdata: {e}")
        return pd.DataFrame()


async def renderhtml():
    tdata = await transferdata()
    if tdata.empty:
        print("No data to visualize")
        return

    map_1 = KeplerGl(height=600)
    map_1.add_data(data=tdata, name="Taxi Data Visualization")
    map_1.config = {
        'visState': {
            'filters': [{
                'id': 'time_filter',
                'dataId': 'Taxi Data Visualization',
                'name': ['time_str'],
                'type': 'timeRange',
                'enlarged': True
            }],
            'layers': [{
                'type': 'point',
                'config': {
                    'dataId': 'Taxi Data Visualization',
                    'label': 'Taxi Trajectories',
                    'columns': {
                        'lat': 'latitude',
                        'lng': 'longitude',
                        'time': 'time_str'
                    },
                    'isVisible': True,
                    'visConfig': {
                        'opacity': 0.8,
                        'radius': 6,
                        'color': [0, 255, 0],
                    },
                    "colorField": {
                        "name": "devid",
                        "type": "integer"
                    },
                }
            }],
        },
        'mapState': {
            'latitude': 45.7567,
            'longitude': 126.6422,
            'zoom': 10
        },
    }
    htmlfile_name = str(uuid.uuid4()).replace('-', '')[:8] + ".html"
    map_1.save_to_html(file_name=htmlfile_name)
    with open(htmlfile_name, "r", encoding="utf-8") as f:
        result_html = f.read()
    os.remove(htmlfile_name)
    return HTMLResponse(content=result_html)
