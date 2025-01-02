import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from keplergl import KeplerGl
import transbigdata as tbd
import webbrowser
import json

# 数据加载与处理
data = pd.read_csv('onehour.csv', header=None)  # 修改为实际路径

data.columns = ['devid', 'speed', 'latitude', 'longitude','Stime']
data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
data['speed'] = pd.to_numeric(data['speed'], errors='coerce')
data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
data['devid'] = pd.to_numeric(data['devid'], downcast='integer', errors='coerce')
if 'OpenStatus' not in data.columns:
    data['OpenStatus'] = 0  # 默认值为 0
# data['Stime'] = pd.to_datetime(data['Stime'], format='%Y-%m-%d %H:%M:%S').astype(str)
print(data['Stime'].min(), data['Stime'].max())
hrb = gpd.read_file('realmap.json')  # 修改为实际路径
hrb.crs = None
data = tbd.clean_outofshape(data, hrb, col=['longitude', 'latitude'], accuracy=500)
data = tbd.clean_taxi_status(data, col=['devid', 'Stime','OpenStatus'])

# HTML 文件路径
html_file = "taxi_oh.html"

# 检查文件是否存在且非空
if os.path.exists(html_file) and os.path.getsize(html_file) > 0:
    print(f"HTML 文件 '{html_file}' 已存在，直接打开...")
    webbrowser.open(html_file)
else:
    print(f"HTML 文件 '{html_file}' 不存在或为空，生成新的文件...")

    # 创建 Kepler.gl 地图并加载数据
    map_1 = KeplerGl(height=600)
    map_1.add_data(data=data, name="Taxi Data Visualization")
    map_1.config = {
        'visState': {
            'filters': [{
                'id': 'time_filter',
                'dataId': 'Taxi Data Visualization',
                'name': ['Stime'],
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
                        'time': 'Stime'
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

    # 保存到 HTML 文件并打开
    map_1.save_to_html(file_name=html_file)
    config = map_1.config
    with open('kepler_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # 检查过滤器部分
    print(config)
    webbrowser.open(html_file)