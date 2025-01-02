import aioredis

async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url(
        "redis://localhost",  # Redis 地址
        port=6379,            # Redis 端口
        db=0,                 # 数据库索引
        decode_responses=True # 是否将结果解码为字符串
    )
    return redis

