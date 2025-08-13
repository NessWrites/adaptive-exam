from fastapi import FastAPI

app = FastAPI(title="Fuse Adaptive Exam")

@app.get("/")
def read_root():
    return {"message": "Welcome to Fuse Academics Adaptive Exam API"}

# TODO: Add endpoints for exam generation, e.g., /generate-exam with params difficulty, question_type, sub_topic
