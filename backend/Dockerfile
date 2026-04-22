FROM python:3.11-slim


WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements from backend directory
COPY backend/backend-requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt
RUN pip install --no-cache-dir jinja2
# copy application code 
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]