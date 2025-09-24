# backend/main.py
from fastapi import FastAPI
from .app.database.postgresql.connection import engine
from .app.models import models
from .app.routes.students_route import router as students_router
from .app.routes.questions_route import router as questions_router
from .app.routes.test_sessions_route import router as test_sessions_router
from .app.routes.responses_route import router as responses_router
from .app.routes.bayesian_ability_estimates_route import router as bayesian_ability_estimates_router
from .app.routes.question_parameters_route import router as question_parameters_router
from .app.routes.submissions_route import router as submissions_router
from .app.routes.data_upload_route import router as data_upload_router

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bayesian IRT API", version="1.0.0")

# Include routers with prefixes and tags for better organization
app.include_router(students_router, prefix="/students", tags=["Students"])
app.include_router(questions_router, prefix="/questions", tags=["Questions"])
app.include_router(test_sessions_router, prefix="/test_sessions", tags=["Test Sessions"])
app.include_router(responses_router, prefix="/responses", tags=["Responses"])
app.include_router(bayesian_ability_estimates_router, prefix="/bayesian_ability_estimates", tags=["Bayesian Ability Estimates"])
app.include_router(question_parameters_router, prefix="/question_parameters", tags=["Question Parameters"])
app.include_router(submissions_router, prefix="/submissions", tags=["Submissions"])
app.include_router(data_upload_router, prefix="/data", tags=["Data Upload"])
