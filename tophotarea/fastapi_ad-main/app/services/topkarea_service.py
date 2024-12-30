
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
    "host": "law.conetop.cn",       # ���ݿ��ַ
    "port": 5432,              # ���ݿ�˿�
    "database": "harbintrips", # ���ݿ�����
    "user": "zhongtai",   # ���ݿ��û���
    "password": "zt123!" # ���ݿ�����
}


def getClustersByGrahamScanService(time:int)->List[TopkAreaClusters_ByGrahamScan]:
    objects=[]
    try:

        #���ӵ� PostgreSQL ���ݿ�
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        # ��ѯ topkarea_graham ������
        cursor.execute('SELECT id, longitude, latitude, time, clusterid  FROM topkarea_graham WHERE time = %s ', (time,))  # ʹ�ò�������ѯ������ SQL ע��
        rows = cursor.fetchall()
        # ������ѯ��������������б�
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

#��ȡʵʱ·��
def getCurrentRoads():
    curoads=[]
    try:
         # ���ӵ� PostgreSQL ���ݿ�
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # ��ѯ topkarea_graham ������
        cursor.execute('SELECT roadid,longitude,latitude,seq,orientation,status FROM topkarea_roads ')  # ʹ�ò�������ѯ������ SQL ע��
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

    #���ľ�γ�� [45.76637,126.67251]
    input_longitude=lng 
    input_latitude =lat
    filtered_data = []
    for entry in objects:
        distance = haversine(input_longitude, input_latitude, entry.longitude, entry.latitude)
        if distance <= 2:
          filtered_data.append(entry)
    return filtered_data

def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # ����뾶����λΪ����
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # ���ؾ��룬��λΪ����
    return distance

def calculate_distance(lon1, lat1, lon2, lat2):
    return math.sqrt((lon1 - lon2)**2 + (lat1 - lat2)**2)

def build_graph(roads):
    graph = Graph()

    # ����һ���ֵ����洢ÿ��roadid�Ĳ�ͬseq
    road_dict = {}

    # ��ÿ��roadid��������
    for road in roads:
        if road.roadid not in road_dict:
            road_dict[road.roadid] = []
        road_dict[road.roadid].append(road)

    # ����ÿ��roadid�ĵ�·
    for road_list in road_dict.values():
        # ��seq����ÿ��roadid�ڵ�seq��˳���
        road_list.sort(key=lambda x: x.seq)
        # ��ͬһ��roadid������ÿ��seq
        for i in range(len(road_list) - 1):
            start = road_list[i]
            end = road_list[i + 1]
            weight = start.get_weight()
            start_key = f"{start.roadid}_{start.seq}"
            end_key = f"{end.roadid}_{end.seq}"
            graph.add_edge(start_key,end_key, weight)

    # ���Ӳ�ͬroadid�����ڵ�·�����������뿪ʼ���Ƿ���ͬ
    for roadid1, road_list1 in road_dict.items():
        for roadid2, road_list2 in road_dict.items():
            if roadid1 != roadid2:
                # ��ȡÿ����·��end���start�㾭γ��
                end_road = road_list1[-1]
                start_road = road_list2[0]
                
                # ���������·�Ķ˵���ͬ����������
                if (end_road.longitude == start_road.longitude) and (end_road.latitude == start_road.latitude):
                    start_key = f"{start_road.roadid}_{start_road.seq}"
                    end_key = f"{end_road.roadid}_{end_road.seq}"
                    weight = end_road.get_weight()
                    graph.add_edge(end_key,start_key, weight)

    return graph

def dijkstra(graph,roads, start, target):
    # Dijkstra �㷨
    dist = {node: float('inf') for node in graph.adj_list}
    dist[start] = 0
    prev = {node: None for node in graph.adj_list}
    priority_queue = [(0, start)]  # (distance, node)

    # Ԥ������ roads ת��Ϊ�ֵ䣬���ڿ��ٲ���
    road_map = {road.flag: road for road in roads}

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)

        # �����ǰ�ڵ��Ѿ���Ŀ��ڵ�
        if current_node == target:
            path = []
            while prev[current_node] is not None:
                path.append(current_node)
                current_node = prev[current_node]
            path.append(start)
            return path[::-1], dist[target]

        # �����ھӽڵ�ľ���
        for neighbor, weight in graph.get_neighbors(current_node):
            current_road = road_map.get(current_node)  # ֱ��ͨ�� flag ��ȡ road
            neighbor_road = road_map.get(neighbor)    # ֱ��ͨ�� flag ��ȡ road
            if current_road and neighbor_road:
                # ��������֮��ĵ������
                geo_distance = haversine(
                    current_road.latitude, current_road.longitude,
                    neighbor_road.latitude, neighbor_road.longitude
                )
                # ����״̬��������
                ##weight_factor = get_weight_by_status(current_road["status"])
                total_distance = current_dist + geo_distance * weight

                # ����ҵ�����·��������
                if neighbor in dist:
                  if total_distance < dist[neighbor]:
                    dist[neighbor] = total_distance
                    prev[neighbor] = current_node
                    heapq.heappush(priority_queue, (total_distance, neighbor))

    return None, float('inf')  # ���û���ҵ�·��

#·���滮
def selectbestpath(lat:float,lng:float):
    clusters=searchClustersByEuclideanDistance(lat,lng)
    #�����������ŵ��ͽ��ĵ�·��
    #���ص�·����
    roads=[]
    # ���ӵ� PostgreSQL ���ݿ�
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
    #�ҵ������ڵ�·��
    for road in roads:
            distance = calculate_distance(lng,lat,road.longitude, road.latitude)
            if distance<car_min_distance:
                car_min_distance=distance
                carroad=road

    #car_road=roads

    allpath=[]
    alldistanceop=[]
    for cluster in clusters: #��������
        
        closets_road=None
        min_distance=float('inf')
        if cluster.clusterid in {50, 41 ,25, 63, 81}:
        #���ݴ����ҵ��丽����·��
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

     # �ҵ� alldistanceop ����С·��������
    min_distance_index = alldistanceop.index(min(alldistanceop))

     # ���ض�Ӧ���·��
    shortest_path = allpath[min_distance_index]
    filtered_roads = [road for road in roads if road.flag in shortest_path]
    filtered_roads_sorted = sorted(filtered_roads, key=lambda road: shortest_path.index(road.flag))

    return filtered_roads_sorted


     
