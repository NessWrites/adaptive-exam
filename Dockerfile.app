# Use an official Python runtime as a parent image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for numpy/scipy/psycopg2 and friends
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only minimal app requirements to keep image small and portable
COPY requirements-app.txt ./
RUN pip install --no-cache-dir -r requirements-app.txt

# Copy project
COPY . .

# Streamlit config for headless inside container
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# Default envs (can be overridden via compose)
ENV STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

# Run Streamlit app (pointing to the v3 adaptive test app)
CMD ["streamlit", "run", "tests/next_question_selection/v3/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
