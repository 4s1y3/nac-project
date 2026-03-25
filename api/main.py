from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from redis_client import get_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    await get_redis()
    yield
    await close_pool()
    await close_redis()

app = FastAPI(title="NAC Policy Engine", lifespan=lifespan)

from routers import auth, authorize, accounting, users, sessions

app.include_router(auth.router)
app.include_router(authorize.router)
app.include_router(accounting.router)
app.include_router(users.router)
app.include_router(sessions.router)

@app.get("/")
async def root():
    return {"message": "NAC Policy Engine is running"}

@app.get("/health")
async def health():
    pool = await get_pool()
    redis = await get_redis()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    pong = await redis.ping()
    return {"status": "ok", "db": True, "redis": pong}