from fastapi import APIRouter, Depends
from pymongo.database import Database

from ..database import get_db


router = APIRouter()


@router.get("/", response_model=list[dict])
def list_logs(limit: int = 100, db: Database = Depends(get_db)):
    items = db["logs"].find().sort("created_at", -1).limit(max(1, min(limit, 1000)))
    out = []
    for it in items:
        out.append(
            {
                "id": str(it.get("_id")),
                "level": it.get("level"),
                "message": it.get("message"),
                "context": it.get("context"),
                "created_at": it.get("created_at"),
            }
        )
    return out


