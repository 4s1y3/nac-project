import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None