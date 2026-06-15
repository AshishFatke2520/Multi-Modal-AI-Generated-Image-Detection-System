from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import get_current_user
from app.core.database import db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HistoryItem(BaseModel):
    id: str
    filename: str
    timestamp: datetime
    verdict: str
    final_score: float

@router.get("/", response_model=List[HistoryItem])
async def read_history(current_user = Depends(get_current_user)):
    user_id = str(current_user.id)
    cursor = db.db.history.find({"user_id": user_id}).sort("timestamp", -1)
    
    results = []
    async for document in cursor:
        results.append(HistoryItem(
            id=str(document["_id"]),
            filename=document["filename"],
            timestamp=document["timestamp"],
            verdict=document["verdict"],
            final_score=document["final_score"]
        ))
    return results

@router.delete("/")
async def clear_history(current_user = Depends(get_current_user)):
    user_id = str(current_user.id)
    result = await db.db.history.delete_many({"user_id": user_id})
    return {"message": f"Deleted {result.deleted_count} logs"}
