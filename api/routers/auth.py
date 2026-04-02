from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from database import get_pool
from redis_client import get_redis

router = APIRouter()

RATE_LIMIT = 5
BLOCK_TIME = 300

class AuthRequest(BaseModel):
    username: str
    password: str | None = None
    calling_station_id: str | None = None
    method: str = "PAP"  # PAP (password), MAB (mac)

@router.post("/auth")
async def authenticate(request: AuthRequest):
    redis = await get_redis()
    user_key = request.username or request.calling_station_id
    if not user_key:
        raise HTTPException(status_code=400, detail="username or calling_station_id required")

    block_key = f"block:{user_key}"
    fail_key = f"fails:{user_key}"

    if await redis.exists(block_key):
        raise HTTPException(status_code=403, detail="Too many failed attempts")

    pool = await get_pool()
    async with pool.acquire() as conn:
        if request.method.upper() == "MAB":
            row = await conn.fetchrow(
                "SELECT username FROM radcheck WHERE username=$1 AND attribute='MAB-Password'",
                request.calling_station_id
            )
            if not row:
                # Bilinmeyen MAC → fail sayacını artır, ardından reddet
                fails = await redis.incr(fail_key)
                await redis.expire(fail_key, BLOCK_TIME)
                if int(fails) >= RATE_LIMIT:
                    await redis.set(block_key, 1, ex=BLOCK_TIME)
                    raise HTTPException(status_code=403, detail="Too many failed attempts")
                raise HTTPException(status_code=401, detail="Unknown MAC")
            # MAC DB'de kayıtlı → kabul et
            await redis.delete(fail_key)
            return {"status": "accept", "username": row["username"], "auth_method": "MAB"}

        # PAP / CHAP
        if not request.password:
            raise HTTPException(status_code=400, detail="password required for PAP/CHAP")
        row = await conn.fetchrow(
            "SELECT value FROM radcheck WHERE username=$1 AND attribute='Bcrypt-Password'",
            request.username
        )
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    password_match = bcrypt.checkpw(
        request.password.encode("utf-8"),  # type: ignore[union-attr]  # guard yukarıda
        row["value"].encode("utf-8")
    )

    if not password_match:
        fails = await redis.incr(fail_key)
        await redis.expire(fail_key, BLOCK_TIME)
        if int(fails) >= RATE_LIMIT:
            await redis.set(block_key, 1, ex=BLOCK_TIME)
            raise HTTPException(status_code=403, detail="Too many failed attempts")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await redis.delete(fail_key)
    return {"status": "accept", "username": request.username, "auth_method": request.method.upper()}