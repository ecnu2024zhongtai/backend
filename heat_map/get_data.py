from pymongo import MongoClient
import pandas as pd
import config

def get_data_from_mongdb():
# 连接到 MongoDB
    client = MongoClient(config.MONGODB_HOST)
    # 选择数据库
    db = client[config.CLIENT_NAME]
    # 选择集合
    collection = db[config.DB_NAME]
    # 查询数据
    documents = collection.find().limit(10000)
    df = pd.DataFrame(documents)
    return df