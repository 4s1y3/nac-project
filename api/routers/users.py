from fastapi import APIRouter
from database import get_pool
from redis_client import get_redis
import json

router = APIRouter()

@router.get("/users")
async def get_users():
    pool = await get_pool()
    redis = await get_redis()

    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT username, groupname FROM radusergroup ORDER BY username")

    sessions = await redis.mget(*await redis.keys("session:*")) if await redis.keys("session:*") else []
    active = {json.loads(s)["username"] for s in sessions if s}

    return {"users":[
        {
            "username": u["username"],
            "group": u["groupname"],
            "status": "online" if u["username"] in active else "offline"
        } for u in users
    ]}