from app.db.postgresql import get_pgdb


async def get_top_ten_locations():
    pg_conn = await get_pgdb()

    # 编写查询语句获取前十条 location
    select_query = "SELECT location FROM processed_data LIMIT 10"
    rows = await pg_conn.fetch(select_query)

    locations = [row[0] for row in rows]

    # 关闭数据库连接
    pg_conn.close()

    return locations