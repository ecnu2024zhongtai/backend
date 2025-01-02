import requests
import csv
from datetime import datetime

# 设置 API URL
api_url = "http://law.conetop.cn:8005/api/v1/trips/recent/1hour"

# 设置输出文件
output_file = "onehour.csv"

# 发送 GET 请求获取数据
try:
    response = requests.get(api_url)
    response.raise_for_status()  # 检查请求是否成功
    data = response.json()  # 解析 JSON 数据
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
    exit(1)

# 检查数据格式是否正确
if not isinstance(data, list):
    print("数据格式不正确，期望为列表类型。")
    exit(1)

# 打开 CSV 文件准备写入
with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    # 写入 CSV 文件头
    # csv_writer.writerow(["devid", "speed", "latitude", "longitude", "timestamp"])

    # 遍历数据并写入 CSV
    for item in data:
        devid = item.get("devid")
        speed = item.get("speed")
        lat = item.get("lat")
        lon = item.get("lon")
        tms = item.get("tms")

        if devid is not None and speed is not None and lat is not None and lon is not None and tms is not None:
            try:
                # 将时间戳转换为日期时间字符串
                time_str = datetime.fromtimestamp(tms).strftime("%Y-%m-%d %H:%M:%S")
                # 写入 CSV 文件
                csv_writer.writerow([devid, speed, lat, lon, time_str])
            except Exception as e:
                print(f"时间转换错误: {e}")

print(f"数据已成功提取并保存到 {output_file}")
