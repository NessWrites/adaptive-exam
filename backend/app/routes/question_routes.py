from fastapi import APIRouter

router = APIRouter()

@router.get("/questions")
def get_questions():
    return {"message": "List of questions will go here"}
