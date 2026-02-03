# Adaptive Examination System

An intelligent adaptive examination system that evaluates candidates across two dimensions: **Mathematics** and **Technical Skills**. The system dynamically adjusts question difficulty based on candidate performance to provide accurate skill assessment.

##  Overview

This system implements an adaptive testing mechanism that:
- Evaluates candidates on Math and Technical dimensions
- Adjusts question difficulty in real-time based on performance
- Provides comprehensive analytics and results

##  Project Structure
```
.
├── ai_models/              # AI model configurations and implementations
├── backend/
│   ├── app/
│   │   ├── core/          # Core configurations and utilities
│   │   ├── database/      # Database connections and setup
│   │   ├── models/        # Data models and schemas
│   │   ├── routes/        # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic layer
│   │   ├── utils/         # Utility functions
│   │   ├── __init__.py
│   │   └── main.py        # FastAPI application entry point
│   └── requirements.txt   # Backend dependencies
├── data/                  # Data files and datasets
├── docs/                  # Documentation
├── frontend/              # Streamlit frontend application
├── generator/             # Question generation modules
├── quiz_database_setup/   # Database initialization scripts
├── results/               # IRT values
├── scripts/               # R scripts
├── tests/                 # Test suite (planned)
├── .gitignore
├── docker-compose.yml     # Docker configuration (planned)
├── README.md
└── requirements.txt       # Project dependencies
```

##  Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** PostgreSQL

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database

### Installation

1. **Clone the repository:**
```bash
   git clone <repository-url>
   cd adaptive-exam
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Run the backend:**
```bash
   uvicorn backend.app.main:app --reload
```
   The API will be available at `http://localhost:8000`

4. **Run the frontend:**
```bash
   streamlit run frontend/streamlit_app.py
```
   The interface will be available at `http://localhost:8501`

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_database

# AI Model Configuration
GROK_API_KEY=your_api_key_here

# Frontend Configuration
STREAMLIT_SERVER_PORT=8501
```

##  Database Schema

The system uses PostgreSQL for:
- Question bank storage
- Test sessions and responses
- Results and analytics
