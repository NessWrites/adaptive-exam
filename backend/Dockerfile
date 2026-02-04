FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements from backend directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ai_models from root
# COPY ./ai_models /app/ai_models

# Copy backend app
COPY ./backend /app/backend

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]