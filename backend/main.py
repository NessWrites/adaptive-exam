from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from question_routes import router as question_router

# Create tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include question router
app.include_router(question_router)

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Student Endpoints
@app.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students", response_model=list[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students

@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Question Endpoints
@app.post("/questions", response_model=schemas.QuestionOut)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    db_question = models.Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@app.get("/questions", response_model=list[schemas.QuestionOut])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    return questions

@app.get("/questions/{question_id}", response_model=schemas.QuestionOut)
def get_question(question_id: str, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

# Test Session Endpoints
@app.post("/test_sessions", response_model=schemas.TestSessionOut)
def create_test_session(session: schemas.TestSessionCreate, db: Session = Depends(get_db)):
    db_session = models.TestSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# Response Endpoints
@app.post("/responses", response_model=schemas.ResponseOut)
def create_response(response: schemas.ResponseCreate, db: Session = Depends(get_db)):
    db_response = models.Response(**response.dict())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

# Bayesian Ability Estimate Endpoints
@app.post("/bayesian_ability_estimates", response_model=schemas.BayesianAbilityEstimateOut)
def create_bayesian_ability_estimate(estimate: schemas.BayesianAbilityEstimateCreate, db: Session = Depends(get_db)):
    db_estimate = models.BayesianAbilityEstimate(**estimate.dict())
    db.add(db_estimate)
    db.commit()
    db.refresh(db_estimate)
    return db_estimate

# Question Parameter Endpoints
@app.post("/question_parameters", response_model=schemas.QuestionParameterOut)
def create_question_parameter(param: schemas.QuestionParameterCreate, db: Session = Depends(get_db)):
    db_param = models.QuestionParameter(**param.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param

# Submission Endpoints
@app.post("/submissions", response_model=schemas.SubmissionOut)
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    db_submission = models.Submission(**submission.dict())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission