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
    query = "SELECT dayid, lat_index, lon_index, time_index, ppdensity, trip_count FROM forecast_dataset WHERE dayid = %s"
    df = pd.read_sql(query, conn, params=(dayid,))
    conn.close()
    return df


datas = load_data_from_db(5)
print(len(datas))
print(datas.head())

# Define Dataset
class TripDataset(Dataset):
    def __init__(self, df):
        self.df = df

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        input_tensor = torch.tensor([row['dayid'], row['lat_index'], 
                                     row['lon_index'], row['time_index'], 
                                     row['ppdensity']], dtype=torch.float32)
        target = torch.tensor(row['trip_count'], dtype=torch.float32)
        return input_tensor, target
    
# Create DataLoader
dataset = TripDataset(datas)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

# Initialize ConvLSTM Model
input_dim = 5  # dayid, lat_index, lon_index, time_index, ppdensity
hidden_dim = [16]
kernel_size = (3, 3)
num_layers = 1
model = ConvLSTM(input_dim, hidden_dim, kernel_size, num_layers, batch_first=True, bias=True, return_all_layers=False)

# Check for CUDA
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Define Loss Function and Optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training Loop
num_epochs = 10

for epoch in range(num_epochs):
    for inputs, targets in dataloader:
        inputs, targets = inputs.to(device), targets.to(device)

        # 打印输入张量的形状以进行调试
        print(f'原始输入张量的形状: {inputs.shape}')
        
        inputs = inputs.unsqueeze(1).unsqueeze(3).unsqueeze(4)  # Reshape to (batch_size, seq_len, channels, height, width)
        targets = targets.unsqueeze(1).unsqueeze(2).unsqueeze(3).unsqueeze(4)  # Reshape to match model output
        
        # 打印调整后的输入张量的形状以进行调试
        print(f'调整后的输入张量的形状: {inputs.shape}')

        # Forward pass
        outputs, _ = model(inputs)
                # 打印输出张量和目标张量的形状以进行调试
        print(f'输出张量的形状: {outputs[-1].shape}')
        print(f'目标张量的形状: {targets.shape}')
        # 调整输出张量和目标张量的形状以匹配
        outputs = outputs[-1].view(outputs[-1].size(0), -1)
        targets = targets.view(targets.size(0), -1)

        # 计算损失
        loss = criterion(outputs, targets)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# Save the model
torch.save(model.state_dict(), 'convlstm_5_01.pth')
