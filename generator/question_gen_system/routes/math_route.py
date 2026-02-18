from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/mathematics")
async def generator():
    return {"question": "This is a math question generator."}
