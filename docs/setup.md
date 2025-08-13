# Local Setup Guide for Adaptive Exam System

## Prerequisites
- Python 3.10+
- pip
- MongoDB running locally or accessible via URI
- PostgreSQL running locally or accessible via URI
- (Optional) Streamlit for frontend

## Clone Repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

## Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

## MongoDB Setup
- Make sure MongoDB is running locally or set  in your environment:
```bash
export MONGO_URI="mongodb://localhost:27017"
```

## PostgreSQL Setup
- Make sure PostgreSQL is running locally or set :
```bash
export POSTGRES_URI="postgresql://user:password@localhost/dbname"
```
- (Optional) Create the database if it does not exist:
```bash
createdb dbname
```

## Run Backend
```bash
uvicorn backend.main:app --reload
```
- Access the health check at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Run Frontend (Optional)
```bash
streamlit run frontend/streamlit_app.py
```

## Notes
- Ensure the virtual environment is activated whenever working on the project.
- Add any new dependencies to  and reinstall in the virtual environment.

