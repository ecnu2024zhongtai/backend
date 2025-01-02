import asyncpg


DATABASE_URL = "postgresql://zhongtai:zt123!@localhost/harbintrips"

async def get_pgdb():
    return await asyncpg.connect(DATABASE_URL)