
## 本项目将提供以下服务：
### 人口密度数据服务

### 哈尔滨历史打车需求数据服务

### 哈尔滨未来十分钟打车需求预测服务

## 需求预测

### 目的
预测未来十分钟哈尔滨各区域的打车需求

### 实现步骤
#### 数据处理
##### 将匹配后数据集加载至MongoDB数据库中
详细代码见文件 '[匹配后打车订单数据处理](dataset_script/mached_trips_load_to_mongodb.ipynb)'
##### 将原始数据集加载至PostgreSql数据库中
详细代码见文件 '[原始出租车轨迹数据处理](dataset_script/origin_trips_load_to_postgresql.ipynb)'
##### 将人口密度数据加载至PostgreSql数据库中
详细代码见文件 '[人口密度数据处理](dataset_script/harbin_population_density_to_pg.ipynb)'

#### 数据转换
按照人口密度格栅数据划分，将原始数据集转换为栅格数据集

提取出栅格数据集的经纬度
```
SELECT longitude FROM harbinpp group by longitude order BY longitude ASC limit 2;
SELECT longitude FROM harbinpp group by longitude order BY longitude DESC limit 2;
SELECT latitude FROM harbinpp group by latitude order BY latitude ASC limit 2;
SELECT latitude FROM harbinpp group by latitude order BY latitude DESC limit 2;
```
获得格栅特征结果
> 45.40416666666613  45.41249999999946  0.008333333 45.4 
46.09583333333279  46.08749999999946  0.008333333 46.1
127.05416666666545 127.04583333333213 0.008333333 127.058333333
126.0874999999988  126.09583333333212 0.008333333 126.083333333
### 数据建模

为harbinpp表添加格栅划分字段，并更新数据
```
ALTER TABLE harbinpp
ADD COLUMN lon_index INTEGER,
ADD COLUMN lat_index INTEGER;
UPDATE harbinpp
SET log_index = CEIL((longitude - 126.083333333) / 0.008333333),
    lat_index = CEIL((latitude - 45.4) / 0.008333333);
```
为trip_se4表添加格栅划分字段，同理其他表
```
ALTER TABLE trip_se4
ADD COLUMN lon_index INTEGER,
ADD COLUMN lat_index INTEGER,
ADD COLUMN time_index INTEGER;

#1420243200  1.03
#1420329600  1.04
#1420416000  1.05
#1420502400  1.06
#1420588800  1.07

UPDATE trip_se4
SET lon_index = CEIL((st_lon - 126.083333333) / 0.008333333),
    lat_index = CEIL((st_lat - 45.4) / 0.008333333),
    time_index = CEIL((st_timestamp - 1420329600) / 600);

```

构建数据集
```SQL
CREATE TABLE IF NOT EXISTS forecast_dataset (
    dayid INTEGER,
    lon_index INTEGER,
    lat_index INTEGER,
    time_index INTEGER,
    PRIMARY KEY (dayid, lon_index, lat_index, time_index)
);

INSERT INTO forecast_dataset (dayid, lon_index, lat_index, time_index)
SELECT 
    4,  
    lon_index, 
    lat_index, 
    time_index
FROM 
    trip_se4
GROUP BY 
    lon_index, 
    lat_index, 
    time_index;

ALTER TABLE forecast_dataset
ADD COLUMN ppdensity INTEGER;

UPDATE forecast_dataset fd
SET ppdensity = hp.population_density
FROM harbinpp hp
WHERE fd.lon_index = hp.lon_index
  AND fd.lat_index = hp.lat_index;
```


### 模型构建

采用ConvLSTM构建模型

模型代码参考:[ConvLSTM_pytorch](https://github.com/ndrplz/ConvLSTM_pytorch)

论文参考：[Convolutional LSTM Network: A Machine Learning
Approach for Precipitation Nowcasting](https://arxiv.org/abs/1506.04214)

![image](https://github.com/user-attachments/assets/8818dee0-a77c-47c9-ac99-94c279574089)


![image](https://github.com/user-attachments/assets/f3262011-9db8-4b81-8ec3-a87bd4242ed2)


![image](https://github.com/user-attachments/assets/43db9399-508a-4de8-8300-0f87354ea982)


2. 模型构建
    1. 模型选择
    2. 模型训练
    3. 模型评估
    3. 模型应用
3. 模型部署
    1. 模型上线
    2. 模型监控
    3. 模型维护
4. 服务化
    1. 服务部署
    2. 服务监控
    3. 服务维护
