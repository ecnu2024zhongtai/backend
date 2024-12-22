import pandas as pd
import ast
from datetime import datetime
import folium
from folium.plugins import HeatMapWithTime
import psycopg2
from psycopg2 import sql
from .get_data import get_data_from_mongdb
import config

def data_cope(data):
    data['timestamp'] = data['timestamp'].apply(ast.literal_eval)
    data['latitudes'] = data['latitudes'].apply(ast.literal_eval)
    data['longitudes'] = data['longitudes'].apply(ast.literal_eval)

    data_exploded = data.apply(lambda x: pd.Series(zip(x['timestamp'], x['longitudes'], x['latitudes'])), axis=1).stack().reset_index(level=1, drop=True)
    data_exploded = data_exploded.apply(pd.Series)
    data_exploded.columns = ['timestamp', 'longitude', 'latitude']
    
    # 合并展开的列与原始 DataFrame 的其他列
    df_final = data.drop(['timestamp', 'longitudes', 'latitudes'], axis=1).join(data_exploded)
    
    # # 将时间戳转换为日期格式
    df_final["timestamp"] = df_final["timestamp"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    df = df_final[['timestamp', 'longitude', 'latitude']].copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df


def save_to_pg(data):
    # 数据库连接参数
    db_params = {
        'dbname': 'real_time_heat_map',
        'user': 'xzh',
        'password': 'xzhxzh',
        'host': 'your_host',
        'port': 'your_port'
    }
    
    # 建立数据库连接
    conn = psycopg2.connect(**db_params)
    
    # 创建一个游标对象
    cur = conn.cursor()
    
    # 将DataFrame数据插入到数据库中
    for index, row in data.iterrows():
        # 构建插入语句
        insert_query = sql.SQL("INSERT INTO your_table (timestamp, longitudes, latitudes) VALUES (%s, %s, %s)")
        # 执行插入语句
        cur.execute(insert_query, (row['timestamp'], row['longitude'], row['latitude']))
    
    # 提交事务
    conn.commit()
    
    # 关闭游标和连接
    cur.close()
    conn.close()



def get_time_indexed_data(data):
    df = data_cope(data)
    time_indexed_data = []
    timestamps = []
    for time, group in df.groupby('timestamp'):
        time_indexed_data.append(group[['latitude', 'longitude']].values.tolist())
        timestamps.append(time.strftime('%Y-%m-%d %H:%M:%S'))

    return time_indexed_data, timestamps


def get_heat_map():
    data = get_data_from_mongdb()
    m = folium.Map(location=[45.75, 126.63], tiles=config.MAP_TILES, attr=config.MAP_ATTR, zoom_start=11)
    time_indexed_data, timestamps = get_time_indexed_data(data)
    hm = HeatMapWithTime(
        time_indexed_data,
        index=timestamps,
        radius=10,
        auto_play=True,
        max_opacity=0.5,
        min_opacity=0.5,
    )
    hm.add_to(m)

    m.get_root().html.add_child(folium.Element('<meta charset="utf-8"/>'))

    m.save(config.MAP_SAVE_PATH)


if __name__ == '__main__':
    get_heat_map()
