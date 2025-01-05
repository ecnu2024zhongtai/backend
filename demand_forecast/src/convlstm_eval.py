import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import psycopg2
from convlstm import ConvLSTM
import os

DATABASE_URL = "postgresql://zhongtai:zt123!@localhost/harbintrips"

def get_pgdb():
    return psycopg2.connect(DATABASE_URL)
    
# 模型参数
input_channels = 2  # 一个通道用于历史打车数据，一个通道用于人口密度分布数据
hidden_dim = [16, 32]  # 每层的隐藏状态通道数
kernel_size = (3, 3)
num_layers = 2
batch_first = True
bias = True
return_all_layers = False

# 初始化 ConvLSTM 模型
model = ConvLSTM(input_dim=input_channels,
                 hidden_dim=hidden_dim,
                 kernel_size=kernel_size,
                 num_layers=num_layers,
                 batch_first=batch_first,
                 bias=bias,
                 return_all_layers=return_all_layers)

# 加载保存的模型权重
# 使用绝对路径加载保存的模型权重
model_path = '/home/dk/Code/Python/backend/demand_forecast/src/convlstm_5_02.pth'
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")

# Check for CUDA
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# 设置模型为评估模式
model.eval()

# 从数据库加载一个时间步的数据
def load_single_time_step(dayid: int, time_index: int):
    conn = get_pgdb()
    query = "SELECT dayid, lat_index, lon_index, time_index, ppdensity, trip_count FROM forecast_dataset WHERE dayid = %s and time_index = %s"
    data = pd.read_sql(query, conn, params=(dayid, time_index,))
    conn.close()
    return data

# 从数据库加载多个时间步的数据
def load_multiple_time_steps(dayid: int, start_time_index: int, num_steps: int):
    conn = get_pgdb()  # 假设 get_pgdb() 是一个返回数据库连接的函数
    query = "SELECT dayid, lat_index, lon_index, time_index, ppdensity, trip_count FROM forecast_dataset WHERE dayid = %s and time_index >= %s and time_index < %s"
    data = pd.read_sql(query, conn, params=(dayid, start_time_index, start_time_index + num_steps))
    conn.close()
    return data

def prepare_single_time_step_data(data):
    array_32x21_demand = np.zeros((32, 21), dtype=int)
    array_32x21_pp = np.zeros((32, 21), dtype=int)
    for point in data.itertuples():
        array_32x21_demand[point.lon_index - 52, point.lat_index - 32] = point.trip_count
        array_32x21_pp[point.lon_index - 52, point.lat_index - 32] = point.ppdensity
    single_time_step_data = [array_32x21_demand.tolist(), array_32x21_pp.tolist()]
    return single_time_step_data

def prepare_multiple_time_steps_data(data, num_steps: int):
    all_time_steps_data = []
    for time_index in range(num_steps):
        array_32x21_demand = np.zeros((32, 21), dtype=int)
        array_32x21_pp = np.zeros((32, 21), dtype=int)
        time_step_data = data[data['time_index'] == time_index]
        for point in time_step_data.itertuples():
            array_32x21_demand[point.lon_index - 52, point.lat_index - 32] = point.trip_count
            array_32x21_pp[point.lon_index - 52, point.lat_index - 32] = point.ppdensity
        single_time_step_data = [array_32x21_demand, array_32x21_pp]  # 保持为 numpy 数组
        all_time_steps_data.append(single_time_step_data)
    return all_time_steps_data

# 加载一个时间步的数据
dayid = 7
time_index = 10
# data = load_single_time_step(dayid, time_index)
# single_time_step_data = prepare_single_time_step_data(data)

start_time_index = 0
data = load_multiple_time_steps(dayid, 0, time_index)
multiple_time_steps_data = prepare_multiple_time_steps_data(data, time_index)


# 将数据转换为 PyTorch 张量，并增加批次维度和时间步维度
# inputs = torch.tensor([[single_time_step_data]], dtype=torch.float32).to(device)
inputs = torch.tensor([multiple_time_steps_data], dtype=torch.float32).to(device)

# 确保输入张量的形状正确
print("Inputs shape:", inputs.shape)  # 应该是 (batch_size, seq_len, channels, height, width)

# 进行预测
with torch.no_grad():
    layer_output_list, last_state_list = model(inputs)
    output = layer_output_list[-1]  # 获取最后一层的输出
    
    # 提取打车需求的通道（假设打车需求是第一个通道）
    output = output[:, :, 0, :, :]  # 提取第一个通道
    # 将预测值乘以1000并去除负数
    output = output * 1000
    output = torch.clamp(output, min=0)  # 将负数转换为0
    output = output.round().int()  # 将小数四舍五入并转换为整数
    # 打印预测结果
    print("Predicted Output shape:", output.shape)
    print("Predicted Output:", output)