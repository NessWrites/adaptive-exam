# Adaptive Exam System

## Overview
An adaptive exam platform that adjusts question difficulty and selection based on the student's performance in real-time.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Databases:** MongoDB, PostgreSQL
- **AI Models:** LangGraph

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Run frontend:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
