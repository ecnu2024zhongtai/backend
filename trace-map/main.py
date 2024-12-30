# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
# from pymongo import MongoClient
# import csv
# from datetime import datetime  # 用于时间戳转换
# from bson import ObjectId
#
#
# # 连接到 MongoDB
# client = MongoClient("mongodb://law.conetop.cn:27017/")
# print(client.list_database_names())
# db = client["harbintrips"]  # 替换为实际的数据库名称
# print(db.list_collection_names())
# collection = db["trips2_06"]  # 替换为实际的集合名称
# count = collection.count_documents({})
# print(f"文档数量: {count}")
# # 查询数据
#
# # 查询集合中的所有文档
# documents = collection.find()
# output_file = "trace06.csv"
#
# # 打开 CSV 文件准备写入
# with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
#     csv_writer = csv.writer(csvfile)
#     # 写入 CSV 文件头
#     # csv_writer.writerow(["devid", "timestamp", "longitude","latitude"])
#
#     # 遍历每个文档，提取数据
#     for doc in documents:
#         devid = doc.get("devid", None)
#         timestamps = doc.get("timestamp", [])
#         latitudes = doc.get("latitudes", [])
#         longitudes = doc.get("longitudes", [])
#
#         # 确保 devid 存在，且 timestamps, latitudes 和 longitudes 的长度一致
#         if devid and len(timestamps) == len(latitudes) == len(longitudes):
#             for i in range(len(timestamps)):
#                 time_str = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d %H:%M:%S")
#                 csv_writer.writerow([devid, time_str, longitudes[i], latitudes[i]])
#
# print(f"数据已成功提取并保存到 {output_file}")
from pymongo import MongoClient
import csv
from datetime import datetime  # 用于时间戳转换
from bson import ObjectId

# 连接到 MongoDB
client = MongoClient("mongodb://law.conetop.cn:27017/")
print(client.list_database_names())
db = client["harbintrips"]  # 替换为实际的数据库名称
print(db.list_collection_names())
collection = db["trips2_06"]  # 替换为实际的集合名称
count = collection.count_documents({})
print(f"文档数量: {count}")

# 设置输出文件
output_file = "trace06.csv"

# 使用分页处理来减少内存消耗
batch_size = 10000  # 每次处理的文档数量
cursor = collection.find().batch_size(batch_size)

# 打开 CSV 文件准备写入
with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    # 写入 CSV 文件头
    # csv_writer.writerow(["devid", "timestamp", "longitude", "latitude"])

    # 遍历文档，逐个写入文件
    for doc in cursor:
        devid = doc.get("devid", None)
        timestamps = doc.get("timestamp", [])
        latitudes = doc.get("latitudes", [])
        longitudes = doc.get("longitudes", [])

        # 确保 devid 存在，且 timestamps, latitudes 和 longitudes 的长度一致
        if devid and len(timestamps) == len(latitudes) == len(longitudes):
            for i in range(len(timestamps)):
                # time_str = timestamps[i]
                time_str = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d %H:%M:%S")
                # print(time_str)
                # csv_writer.writerow([devid, time_str, longitudes[i], latitudes[i]])
                csv_writer.writerow([devid, time_str, longitudes[i], latitudes[i]])

print(f"数据已成功提取并保存到 {output_file}")