from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/computer-science")
async def generator():
    return {"question": "This is a cs question generator."}
