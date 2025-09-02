from sqlalchemy.orm import Session
import models
import schemas

# Placeholder for business logic
def get_all_questions(db: Session)-> list[schemas.QuestionOut]:
    return db.query(models.Question).all()
