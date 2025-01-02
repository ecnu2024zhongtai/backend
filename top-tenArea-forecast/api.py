from fastapi import FastAPI
import psycopg2
import os
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/top-ten-locations")
def get_top_ten_locations():
    try:
        logging.debug("Trying to connect to the database...")
        pg_conn = psycopg2.connect(
            host="law.conetop.cn",
            port=5432,
            database="harbintrips",
            user="zhongtai",
            password="zt123!"
        )
        logging.debug("Connected to the database successfully.")
        pg_cursor = pg_conn.cursor()

        # 编写查询语句获取前十条 location
        select_query = "SELECT location FROM processed_data LIMIT 10"
        pg_cursor.execute(select_query)
        results = pg_cursor.fetchall()

        locations = [row[0] for row in results]

        # 关闭游标和连接
        pg_cursor.close()
        pg_conn.close()

        return locations
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": "Internal Server Error"}

# @app.get("/top-ten-locations")
# def get_top_ten_locations():
#     pg_conn = psycopg2.connect(
#         host=os.getenv("law.conetop.cn"),
#         port=int(os.getenv("5432")),
#         database=os.getenv("harbintrips"),
#         user=os.getenv("zhongtai"),
#         password=os.getenv("zt123!")
#     )
#     pg_cursor = pg_conn.cursor()
#
#     # 编写查询语句获取前十条 location
#     select_query = "SELECT location FROM processed_data LIMIT 10"
#     pg_cursor.execute(select_query)
#     results = pg_cursor.fetchall()
#
#     dic = {}
#
#     # 遍历结果，计算并打印每个location中time_XX数据资源的和
#     for row in results:
#         location = row[0]
#         time_sum = 0
#         for i in range(1, 24):  # 对应time_00到time_23字段的索引范围
#             value = row[i]
#             if value is not None:  # 判断值是否为None，只有不为None时才进行累加
#                 time_sum += value
#         print(f"Location: {location}, Time Data Sum: {time_sum}")
#         dic[location] = time_sum
#
#
#     # 关闭游标和连接
#     pg_cursor.close()
#     pg_conn.close()
#
#     return dic

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)