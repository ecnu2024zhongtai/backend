
## 项目介绍
这个项目是用于后端定时任务，定时是更新数据，自动清洗数据等。
使用AirFlow实现
## 项目结构


## 项目启动

### 安装部署AirFlow
```
conda create -n airflow python=3.12
conda activate airflow
pip install apache-airflow
```

#### 初始化数据库
```
airflow db init
```

#### 创建用户
```
airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --password admin123
```

#### 添加airflow.service
```
[Unit]
Description=Airflow Service
After=network.target

[Service]
User=dk
Group=dk
Environment="PATH=/path/to/your/anaconda3/bin"
ExecStart=/bin/bash -c 'source /path/to/your/anaconda3/etc/profile.d/conda.sh && conda activate airflow && airflow webserver --port 8800'
ExecStartPost=/bin/bash -c 'source /path/to/your/anaconda3/etc/profile.d/conda.sh && conda activate airflow && airflow scheduler'
Restart=always

[Install]
WantedBy=multi-user.target
```
#### 重新加载systemd守护进程：
```
sudo systemctl daemon-reload
```
#### 启动并启用服务：
```
sudo systemctl start airflow
sudo systemctl enable airflow
```
#### 检查服务状态：
```
sudo systemctl status airflow
```

### DAGS 启用并管理
安装部署完AirFlow后，
启动AirFlow，以及Scheduler
将本项目dags/目录下脚本复制到AirFlow的dags/目录下，
并在web管理界面启动dags
![image](https://github.com/user-attachments/assets/cf006dc7-7aae-4506-b0a1-046af8c70f2f)
