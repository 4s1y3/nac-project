from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_pool

router = APIRouter()

class AuthorizeRequest(BaseModel):
    username: str
    calling_station_id: str | None = None

@router.post("/authorize")
async def authorize(request: AuthorizeRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_group = await conn.fetchrow(
            "SELECT groupname FROM radusergroup WHERE username=$1 ORDER BY priority LIMIT 1",
            request.username
        )
        if not user_group:
            raise HTTPException(status_code=404, detail="no group")

        rows = await conn.fetch(
            """
            SELECT attribute, op, value
            FROM radgroupreply WHERE groupname=$1
            UNION ALL
            SELECT attribute, op, value
            FROM radreply WHERE username=$2
            """,
            user_group["groupname"], request.username
        )

    if not rows:
        raise HTTPException(status_code=404, detail="no attributes")

    attrs = [{"attribute": r["attribute"], "op": r["op"], "value": r["value"]} for r in rows]
    return {"status":"accept", "username": request.username, "group": user_group["groupname"], "reply": attrs}