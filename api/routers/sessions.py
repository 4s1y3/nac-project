from fastapi import APIRouter
from redis_client import get_redis
import json

router = APIRouter()

@router.get("/sessions/active")
async def get_active_sessions():
    redis = await get_redis()
    
    keys = await redis.keys("session:*")
    
    if not keys:
        return {"active_sessions": [], "count": 0}
    
    sessions = []
    for key in keys:
        data = await redis.get(key)
        if data:
            session = json.loads(data)
            ttl = await redis.ttl(key)
            session["ttl_seconds"] = ttl
            sessions.append(session)
    
    return {
        "active_sessions": sessions,
        "count": len(sessions)
    }