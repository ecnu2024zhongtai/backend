import app.services.trip_service as TripService
from datetime import datetime
import pandas as pd
import geopandas as gpd
import transbigdata as tbd
import uuid
import os
from keplergl import KeplerGl

async def loaddata():
    records = await TripService.get_recent_trips_from_redis()
    results = []
    for record in records:
        devid = record.devid
        speed = record.speed
        lat = record.lat
        lon = record.lon
        tms = record.tms
        if devid is not None and speed is not None and lat is not None and lon is not None and tms is not None:
            try:
                time_str = datetime.fromtimestamp(tms).strftime("%Y-%m-%d %H:%M:%S")
                result = {
                    "devid": devid,
                    "speed": speed,
                    "latitude": lat,
                    "longitude": lon,
                    "time_str": time_str
                }
                results.append(result)
            except Exception as e:
                print(f"时间转换错误: {e}")
    return results

async def transferdata():
    results = await loaddata()
    dfdata = pd.DataFrame(results, columns=['devid', 'speed', 'latitude', 'longitude', 'time_str'])
    dfdata['longitude'] = pd.to_numeric(dfdata['longitude'], errors='coerce')
    dfdata['speed'] = pd.to_numeric(dfdata['speed'], errors='coerce')
    dfdata['latitude'] = pd.to_numeric(dfdata['latitude'], errors='coerce')
    dfdata['devid'] = pd.to_numeric(dfdata['devid'], downcast='integer', errors='coerce')
    if 'OpenStatus' not in dfdata.columns:
        dfdata['OpenStatus'] = 0  # 默认值为 0
    
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    # 去除索引
    dfdata.reset_index(drop=True, inplace=True)
    
    hrb = gpd.read_file('realmap.json')  # 修改为实际路径
    hrb.crs = None
    dfdata = tbd.clean_outofshape(dfdata, hrb, col=['longitude', 'latitude'], accuracy=500)
    dfdata = tbd.clean_taxi_status(dfdata, col=['devid', 'time_str','OpenStatus'])
    return dfdata

async def renderhtml():
    tdata = await transferdata()
    
    # 打印数据类型和内容以进行调试
    print(f"数据类型: {type(tdata)}")
    print(f"数据内容: {tdata.head()}")
    tdata = pd.DataFrame(tdata.values, columns=tdata.columns)
    print(f"重置后数据内容: {tdata.head()}")

    # 创建 Kepler.gl 地图并加载数据
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
    # 保存到 HTML 文件并打开
    map_1.save_to_html(file_name=htmlfile_name)

    # 读取 HTML 文件并返回其内容
    with open(htmlfile_name, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    return html_content
