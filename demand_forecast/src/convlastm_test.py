import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import psycopg2
from convlstm import ConvLSTM
DATABASE_URL = "postgresql://zhongtai:zt123!@localhost/harbintrips"

def get_pgdb():
    return psycopg2.connect(DATABASE_URL)

def load_data_from_db(dayid: int):
    conn = get_pgdb()
    query = "SELECT dayid, lat_index, lon_index, time_index, ppdensity, trip_count FROM forecast_dataset WHERE dayid = %s and time_index = %s"
    
    dayDataset = []
    for i in range(144):
        seqData = pd.read_sql(query, conn, params=(dayid, i,))
        dayDataset.append(seqData)

    conn.close()
    return dayDataset


def load_day_dataset():
    # 4,5,6
    all_bach_dataset = []
    all_targets = []
    for i in range(4,7):
        datas = load_data_from_db(i)
        one_day_dataset = []
        one_day_targets = []
        if(len(datas) != 144):
            print("data length is not 144:", len(datas))
            continue
        for data in datas:
            print(data)
            one_sequence_data = []
            array_32x21_demand = np.zeros((32, 21), dtype=int)
            array_32x21_pp = np.zeros((32, 21), dtype=int)
            for point in data.itertuples():
                # 填充数据到数组中
                print(point)
                print(point.lon_index)
                
                array_32x21_demand[point.lon_index - 52, point.lat_index - 32] = point.trip_count
                array_32x21_pp[point.lon_index - 52, point.lat_index - 32] = point.ppdensity

            # 打印填充后的数组
            one_sequence_data = [array_32x21_demand.tolist(), array_32x21_pp.tolist()]
            one_day_dataset.append(one_sequence_data)
            one_day_targets.append(array_32x21_demand.tolist())  # 使用打车需求作为目标数据

        all_bach_dataset.append(one_day_dataset)
        all_targets.append(one_day_targets)
    return all_bach_dataset, all_targets


# 51, 83 lon_index 83 - 51 = 32 height
# 31, 52 lat_index 52 - 31 = 21 weight

dataset = load_day_dataset()
print(dataset)
print(len(dataset))
