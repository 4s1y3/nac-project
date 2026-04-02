from fastapi import APIRouter
from redis_client import get_redis
import json 

router = APIRouter()

@router.get("/sessions/active")
async def get_active_sessions():
    r = await get_redis()
    keys = await r.keys("session:*")
    sessions = []
    for key in keys:
        data = await r.get(key)
        if data:
            s = json.loads(data)
            s["ttl_seconds"] = await r.ttl(key)
            sessions.append(s)
    return {
        "active_sessions": sessions,
        "count": len(sessions)}