## 数据清洗

从 MongoDB 中将原始数据依次读出，统计上车点的经纬度订单信息，只保留小数点后两位，聚合经度（xx.xx0000...，xx.xx9999...）  ×  纬度（xx.xx0000...，xx.xx9999...）四个点围成的区域

```python
# MongoDB连接参数
mongo_host = 'law.conetop.cn'
mongo_port = 27017
mongo_database_name = 'harbintrips'

# 创建MongoDB客户端并连接到数据库
mongo_client = MongoClient(host=mongo_host, port=mongo_port)
mongo_db = mongo_client[mongo_database_name]

mmap = dict()

# 从MongoDB中读取数据并处理
for num in range(3, 8):
    collection_name = f'trips2_{num:02}'
    collection = mongo_db[collection_name]
    cursor = collection.find()
    while True:
        try:
            doc = cursor.next()
            data = pd.DataFrame([doc])  # 将单个文档转换为 DataFrame

            x = data.iloc[0]

            # 以下处理逻辑与之前相同
            if (x['latitudes'] is None or len(x['latitudes']) == 0) or (x['longitudes'] is None or len(x['longitudes']) == 0) or (x['time'] is None or len(x['time']) == 0):
                continue

            latitude = round(x['latitudes'][0], 2)
            longitude = round(x['longitudes'][0], 2)
            time = unix_to_beijing_hour(x['time'][0])

            if (latitude, longitude) not in mmap:
                mmap[(latitude, longitude)] = {}

            if time not in mmap[(latitude, longitude)]:
                mmap[(latitude, longitude)][time] = 0

            mmap[(latitude, longitude)][time] += 1

            print(f'当前该地区{(latitude, longitude)}共有({count_elements(mmap[(latitude, longitude)])})个订单', end=" -> ")
            print(f'时间：{time} 共有', end=' -> ')
            print(f'{mmap[(latitude, longitude)][time]} 个订单')
        except StopIteration:
            print('time error')
            break
            
    print(f'\n\n\n{collection_name}, over\n\n\n')
```

### - 部分输出

```
当前该地区(45.76, 126.6)共有(11)个订单 -> 时间：00 共有 -> 11 个订单
当前该地区(45.77, 126.71)共有(1)个订单 -> 时间：00 共有 -> 1 个订单
当前该地区(45.75, 126.61)共有(23)个订单 -> 时间：00 共有 -> 23 个订单
当前该地区(45.77, 126.65)共有(18)个订单 -> 时间：00 共有 -> 18 个订单
当前该地区(45.74, 126.59)共有(18)个订单 -> 时间：00 共有 -> 18 个订单
当前该地区(45.74, 126.66)共有(15)个订单 -> 时间：00 共有 -> 15 个订单
当前该地区(45.76, 126.59)共有(7)个订单 -> 时间：00 共有 -> 7 个订单
当前该地区(45.75, 126.68)共有(5)个订单 -> 时间：00 共有 -> 5 个订单
当前该地区(45.74, 126.63)共有(9)个订单 -> 时间：00 共有 -> 9 个订单
当前该地区(45.71, 126.55)共有(1)个订单 -> 时间：00 共有 -> 1 个订单
当前该地区(45.74, 126.66)共有(16)个订单 -> 时间：00 共有 -> 16 个订单
当前该地区(45.73, 126.58)共有(5)个订单 -> 时间：00 共有 -> 5 个订单
当前该地区(45.74, 126.67)共有(11)个订单 -> 时间：00 共有 -> 11 个订单
当前该地区(45.75, 126.61)共有(24)个订单 -> 时间：00 共有 -> 24 个订单
当前该地区(45.74, 126.68)共有(6)个订单 -> 时间：00 共有 -> 6 个订单
当前该地区(45.75, 126.65)共有(17)个订单 -> 时间：00 共有 -> 17 个订单
当前该地区(45.76, 126.66)共有(12)个订单 -> 时间：00 共有 -> 12 个订单
当前该地区(45.76, 126.66)共有(13)个订单 -> 时间：00 共有 -> 13 个订单
当前该地区(45.74, 126.63)共有(10)个订单 -> 时间：00 共有 -> 10 个订单
当前该地区(45.73, 126.65)共有(8)个订单 -> 时间：00 共有 -> 8 个订单
当前该地区(45.73, 126.66)共有(2)个订单 -> 时间：00 共有 -> 2 个订单
当前该地区(45.77, 126.61)共有(12)个订单 -> 时间：00 共有 -> 12 个订单
当前该地区(45.77, 126.74)共有(1)个订单 -> 时间：00 共有 -> 1 个订单
当前该地区(45.73, 126.7)共有(14)个订单 -> 时间：00 共有 -> 14 个订单
```

## 存储中间数据到PostgreSQL

表结构为，储存了源数据中所有聚合后的分时段上车点信息

```python
create_table_query = """
CREATE TABLE IF NOT EXISTS processed_data (
    location text,
    time_00 integer,
    time_01 integer,
    time_02 integer,
    time_03 integer,
    time_04 integer,
    time_05 integer,
    time_06 integer,
    time_07 integer,
    time_08 integer,
    time_09 integer,
    time_10 integer,
    time_11 integer,
    time_12 integer,
    time_13 integer,
    time_14 integer,
    time_15 integer,
    time_16 integer,
    time_17 integer,
    time_18 integer,
    time_19 integer,
    time_20 integer,
    time_21 integer,
    time_22 integer,
    time_23 integer,
    PRIMARY KEY (location)
);
"""
```

## 高德API可视化top10的热门打车点

![image-20250103021018640](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20250103021018640.png)

![image-20250103020955753](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20250103020955753.png)