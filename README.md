# Adaptive Examination System

An intelligent adaptive examination system that evaluates candidates across two dimensions: **Mathematics** and **Technical Skills**. The system dynamically adjusts question difficulty based on candidate performance to provide accurate skill assessment, with integrated question paraphrasing and distractor generation capabilities.

##  Overview

This system implements an adaptive testing mechanism that:
- Evaluates candidates on Math and Technical dimensions
- Adjusts question difficulty in real-time based on performance
- Generates question variants through paraphrasing and scenario transformations
- Automatically creates plausible distractors for multiple-choice questions
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
│   │   │   └── qpool_service.py  # QPool API client service
│   │   ├── utils/         # Utility functions
│   │   ├── __init__.py
│   │   └── main.py        # FastAPI application entry point
│   └── requirements.txt   # Backend dependencies
├── data/                  # Data files and datasets
├── docs/                  # Documentation
├── frontend/              # Streamlit frontend application
├── generator/             # Question generation modules
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
- **Question Generation:** QPool API 

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- QPool API service (separate repository)

### Installation

#### 1. Clone the Adaptive Exam Repository
```bash
git clone <repository-url>
cd adaptive-exam
```

#### 2. Set Up QPool API Service

The question generation features require the QPool API service to be running separately.
```bash
# Clone the QPool repository
git clone <qpool-repository-url>
cd qpool

# Follow the QPool repository's README instructions to:
# - Install dependencies
# - Configure environment variables
# - Run the FastAPI server

# The QPool API should be running on http://127.0.0.1:8000
# Verify it's running by visiting http://127.0.0.1:8000/docs
```

**Note:** By default, the adaptive exam system expects QPool API to run on `http://127.0.0.1:8000`. If you need to use a different URL, update the `base_url` in `backend/app/services/qpool_service.py`.

#### 3. Install Adaptive Exam Dependencies
```bash
# Return to the adaptive-exam directory
cd ../adaptive-exam

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the root directory:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_database

# AI Model Configuration
GROK_API_KEY=your_api_key_here

# Frontend Configuration
STREAMLIT_SERVER_PORT=8501
```

#### 5. Run the Backend
```bash
uvicorn backend.app.main:app --reload --port 8001
```

**Note:** The backend runs on port 8001 to avoid conflict with QPool API on port 8000.

The API will be available at `http://localhost:8001`

#### 6. Run the Frontend
```bash
streamlit run frontend/streamlit_app.py
```

The interface will be available at `http://localhost:8501`

### Running Both Services

For a complete setup, you'll need two terminal windows:

**Terminal 1 - QPool API:**
```bash
cd qpool
# Follow QPool's startup instructions
uvicorn main:app --reload  # Example - check QPool README for exact command
```

**Terminal 2 - Adaptive Exam Backend:**
```bash
cd adaptive-exam
uvicorn backend.app.main:app --reload --port 8001
```

**Terminal 3 - Frontend (optional):**
```bash
cd adaptive-exam
streamlit run frontend/streamlit_app.py
```

##  Configuration

### QPool Service Configuration

To modify the QPool API endpoint, edit `backend/app/services/qpool_service.py`:
```python
class QPoolService:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"  # Update this URL if needed
```

Alternatively, you can set environment variables in your `.env` file and modify the service to read from settings.

##  Database Schema

The system uses PostgreSQL for:
- Question bank storage
- Test sessions and responses
- Results and analytics

