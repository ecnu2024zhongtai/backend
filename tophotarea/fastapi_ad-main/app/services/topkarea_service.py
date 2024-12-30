
import datetime
from platform import node
import pandas as pd
from typing import List

from sqlalchemy import null
from sqlalchemy.engine import row
from app.models.topkarea import Graph, TopkAreaClusters_ByGrahamScan  
from app.models.topkarea import Roads  
import psycopg2
import math
import heapq

file_path="C:\\Users\\wujie\\Desktop\\topkarea_graham_202412222251graham.xls"

DB_CONFIG = {
    "host": "law.conetop.cn",       # 数据库地址
    "port": 5432,              # 数据库端口
    "database": "harbintrips", # 数据库名称
    "user": "zhongtai",   # 数据库用户名
    "password": "zt123!" # 数据库密码
}


def getClustersByGrahamScanService(time:int)->List[TopkAreaClusters_ByGrahamScan]:
    objects=[]
    try:

        #连接到 PostgreSQL 数据库
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        # 查询 topkarea_graham 表数据
        cursor.execute('SELECT id, longitude, latitude, time, clusterid  FROM topkarea_graham WHERE time = %s ', (time,))  # 使用参数化查询，避免 SQL 注入
        rows = cursor.fetchall()
        # 遍历查询结果并构建对象列表
        for row in rows:
           obj = TopkAreaClusters_ByGrahamScan(
               id=int(row[0]),
               longitude=float(row[1]),
               latitude=float(row[2]),
               time=float(row[3]),
               clusterid=int(row[4])
           )
           objects.append(obj)
        # df=pd.read_excel("C:\\Users\\wujie\\Desktop\\topkarea_graham_202412222251graham.xls")
        # for _,row in df.iterrows():
        #     if(float(row['time'])==14):
        #        obj=TopkAreaClusters_ByGrahamScan(
        #           id=int(row['id']),
        #           longitude=float(row['longitude']),      
        #           latitude=float(row['latitude']),
        #           time=float(row['time']),
        #           clusterid=int(row['clusterid'])
        #         )
        #        objects.append(obj)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the CSV file: {str(e)}") 
    current_hour=time #datetime.datetime.now().hour

    filtered_data = [obj for obj in objects if obj.time == current_hour]

    return filtered_data

#获取实时路径
def getCurrentRoads():
    curoads=[]
    try:
         # 连接到 PostgreSQL 数据库
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # 查询 topkarea_graham 表数据
        cursor.execute('SELECT roadid,longitude,latitude,seq,orientation,status FROM topkarea_roads ')  # 使用参数化查询，避免 SQL 注入
        rows = cursor.fetchall()
        for row in rows:
           obj=Roads(
               roadid=int(row[0]),
               longitude=float(row[1]),
               latitude=float(row[2]),
               seq=int(row[3]),
               orientation=str(row[4]),
               status=str(row[5])
           )
           curoads.append(obj)

        # df=pd.read_excel("C:\\Users\\wujie\\Desktop\\topkarea_roads_202412262127toparearoads.xls")
        # for _,row in df.iterrows():
        #     obj=Roads(
        #         roadid=int(row['roadid']),
        #         longitude=float(row['longitude']),
        #         latitude=float(row['latitude']),
        #         seq=int(row['seq']),
        #         orientation=str(row['orientation']),
        #         status=str(row['status'])
        #      )
        #     curoads.append(obj)

    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the CSV file: {str(e)}") 
    return curoads

def searchClustersByEuclideanDistance(lat:float,lng:float)->List[TopkAreaClusters_ByGrahamScan]:
    objects=[]
    try:
        connection=psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute('select id,longitude,latitude,time,clusterid from topkarea_graham_center where time=14')
        rows=cursor.fetchall()
        for row in rows:
              obj=TopkAreaClusters_ByGrahamScan(
                 id=int(row[0]),
                 longitude=float(row[1]),      
                 latitude=float(row[2]),
                 time=float(row[3]),
                 clusterid=int(row[4])
              )
              objects.append(obj)

        # df=pd.read_excel("C:\\Users\\wujie\\Desktop\\topkarea_graham_center_202412262309topkareacenter.xls")
        # for _,row in df.iterrows():
        #     if(float(row['time'])==14):
        #        obj=TopkAreaClusters_ByGrahamScan(
        #           id=int(row['id']),
        #           longitude=float(row['longitude']),      
        #           latitude=float(row['latitude']),
        #           time=float(row['time']),
        #           clusterid=int(row['clusterid'])
        #         )
        #        objects.append(obj)


    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the CSV file: {str(e)}") 

    #车的经纬度 [45.76637,126.67251]
    input_longitude=lng 
    input_latitude =lat
    filtered_data = []
    for entry in objects:
        distance = haversine(input_longitude, input_latitude, entry.longitude, entry.latitude)
        if distance <= 2:
          filtered_data.append(entry)
    return filtered_data

def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # 地球半径，单位为公里
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # 返回距离，单位为公里
    return distance

def calculate_distance(lon1, lat1, lon2, lat2):
    return math.sqrt((lon1 - lon2)**2 + (lat1 - lat2)**2)

def build_graph(roads):
    graph = Graph()

    # 创建一个字典来存储每个roadid的不同seq
    road_dict = {}

    # 将每个roadid按序排列
    for road in roads:
        if road.roadid not in road_dict:
            road_dict[road.roadid] = []
        road_dict[road.roadid].append(road)

    # 遍历每个roadid的道路
    for road_list in road_dict.values():
        # 按seq排序，每个roadid内的seq是顺序的
        road_list.sort(key=lambda x: x.seq)
        # 在同一个roadid内连接每个seq
        for i in range(len(road_list) - 1):
            start = road_list[i]
            end = road_list[i + 1]
            weight = start.get_weight()
            start_key = f"{start.roadid}_{start.seq}"
            end_key = f"{end.roadid}_{end.seq}"
            graph.add_edge(start_key,end_key, weight)

    # 连接不同roadid的相邻道路：检查结束点与开始点是否相同
    for roadid1, road_list1 in road_dict.items():
        for roadid2, road_list2 in road_dict.items():
            if roadid1 != roadid2:
                # 获取每条道路的end点和start点经纬度
                end_road = road_list1[-1]
                start_road = road_list2[0]
                
                # 如果两个道路的端点相同，建立连接
                if (end_road.longitude == start_road.longitude) and (end_road.latitude == start_road.latitude):
                    start_key = f"{start_road.roadid}_{start_road.seq}"
                    end_key = f"{end_road.roadid}_{end_road.seq}"
                    weight = end_road.get_weight()
                    graph.add_edge(end_key,start_key, weight)

    return graph

def dijkstra(graph,roads, start, target):
    # Dijkstra 算法
    dist = {node: float('inf') for node in graph.adj_list}
    dist[start] = 0
    prev = {node: None for node in graph.adj_list}
    priority_queue = [(0, start)]  # (distance, node)

    # 预处理：将 roads 转换为字典，便于快速查找
    road_map = {road.flag: road for road in roads}

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)

        # 如果当前节点已经是目标节点
        if current_node == target:
            path = []
            while prev[current_node] is not None:
                path.append(current_node)
                current_node = prev[current_node]
            path.append(start)
            return path[::-1], dist[target]

        # 更新邻居节点的距离
        for neighbor, weight in graph.get_neighbors(current_node):
            current_road = road_map.get(current_node)  # 直接通过 flag 获取 road
            neighbor_road = road_map.get(neighbor)    # 直接通过 flag 获取 road
            if current_road and neighbor_road:
                # 计算两点之间的地理距离
                geo_distance = haversine(
                    current_road.latitude, current_road.longitude,
                    neighbor_road.latitude, neighbor_road.longitude
                )
                # 根据状态调整距离
                ##weight_factor = get_weight_by_status(current_road["status"])
                total_distance = current_dist + geo_distance * weight

                # 如果找到更短路径，更新
                if neighbor in dist:
                  if total_distance < dist[neighbor]:
                    dist[neighbor] = total_distance
                    prev[neighbor] = current_node
                    heapq.heappush(priority_queue, (total_distance, neighbor))

    return None, float('inf')  # 如果没有找到路径

#路径规划
def selectbestpath(lat:float,lng:float):
    clusters=searchClustersByEuclideanDistance(lat,lng)
    #让热门区域附着到就近的道路端
    #加载道路数据
    roads=[]
    # 连接到 PostgreSQL 数据库
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    try:
       cursor.execute("select roadid,longitude,latitude,seq,orientation,status from topkarea_roads ")
       rows = cursor.fetchall()
       for row in rows:
           obj=Roads(
               roadid=int(row[0]),
               longitude=float(row[1]),
               latitude=float(row[2]),
               seq=int(row[3]),
               orientation=str(row[4]),
               status=str(row[5])
            )
           roads.append(obj)
          # df=pd.read_excel("C:\\Users\\wujie\\Desktop\\topkarea_roads_202412262127toparearoads.xls")
          # for _,row in df.iterrows():
          #       obj=Roads(
          #       roadid=int(row['roadid']),
          #       longitude=float(row['longitude']),
          #       latitude=float(row['latitude']),
          #       seq=int(row['seq']),
          #       orientation=str(row['orientation']),
          #       status=str(row['status'])
          #        )
          #       roads.append(obj)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the CSV file: {str(e)}")    
    
    graph=build_graph(roads)


    car_min_distance=float('inf')
    carroad=None
    #找到车所在的路段
    for road in roads:
            distance = calculate_distance(lng,lat,road.longitude, road.latitude)
            if distance<car_min_distance:
                car_min_distance=distance
                carroad=road

    #car_road=roads

    allpath=[]
    alldistanceop=[]
    for cluster in clusters: #热门区域
        
        closets_road=None
        min_distance=float('inf')
        if cluster.clusterid in {50, 41 ,25, 63, 81}:
        #根据簇心找到其附近的路段
          for road in roads:
            distance = calculate_distance(cluster.longitude, cluster.latitude, road.longitude, road.latitude)

            if distance<min_distance:
                min_distance=distance
                closets_road=road
          
          start_key = f"{carroad.roadid}_{carroad.seq}"
          end_key = f"{closets_road.roadid}_{closets_road.seq}"
          path,total_distance =dijkstra(graph,roads,start_key, end_key)
          allpath.append(path)
          alldistanceop.append(total_distance)

     # 找到 alldistanceop 中最小路径的索引
    min_distance_index = alldistanceop.index(min(alldistanceop))

     # 返回对应最短路径
    shortest_path = allpath[min_distance_index]
    filtered_roads = [road for road in roads if road.flag in shortest_path]
    filtered_roads_sorted = sorted(filtered_roads, key=lambda road: shortest_path.index(road.flag))

    return filtered_roads_sorted


     
