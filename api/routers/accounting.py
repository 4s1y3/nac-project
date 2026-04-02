from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import get_pool
from redis_client import get_redis
import json

router = APIRouter()

class AccountingRequest(BaseModel):
    username: str
    session_id: str
    status_type: str
    nas_ip: Optional[str] = None
    session_time: Optional[int] = 0
    input_octets: Optional[int] = 0
    output_octets: Optional[int] = 0
    calling_station_id: Optional[str] = None
    framed_ip: Optional[str] = None
    terminate_cause: Optional[str] = None

@router.post("/accounting")
async def accounting(request: AccountingRequest):
    pool = await get_pool()
    redis = await get_redis()

    if request.status_type == "Start":
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO radacct 
                (username, acctsessionid, nasipaddress, acctstarttime, 
                callingstationid, framedipaddress)
                VALUES ($1, $2, $3::inet, NOW(), $4, $5::inet)
            """,
                request.username,
                request.session_id,
                request.nas_ip,
                request.calling_station_id,
                request.framed_ip
            )

        session_data = {
            "username": request.username,
            "session_id": request.session_id,
            "nas_ip": request.nas_ip or "",
            "calling_station_id": request.calling_station_id or ""
        }
        await redis.set(
            f"session:{request.session_id}",
            json.dumps(session_data),
            ex=86400
        )

    elif request.status_type == "Interim-Update":
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE radacct 
                SET acctsessiontime=$1, acctinputoctets=$2, acctoutputoctets=$3
                WHERE acctsessionid=$4
            """,
                request.session_time,
                request.input_octets,
                request.output_octets,
                request.session_id
            )

    elif request.status_type == "Stop":
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE radacct 
                SET acctstoptime=NOW(), acctsessiontime=$1,
                acctinputoctets=$2, acctoutputoctets=$3,
                acctterminatecause=$4
                WHERE acctsessionid=$5
            """,
                request.session_time,
                request.input_octets,
                request.output_octets,
                request.terminate_cause,
                request.session_id
            )
        await redis.delete(f"session:{request.session_id}")

    return {"status": "ok", "status_type": request.status_type}