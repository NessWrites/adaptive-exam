# Complete MacBook Setup Guide

## Prerequisites
1. Install Docker Desktop for Mac: https://www.docker.com/products/docker-desktop/
2. Clone this repository

## Option A: Everything in Docker (Recommended)
```bash
# 1. Copy your database dump to docker/initdb/seed.sql
# (You already have this from our earlier work)

# 2. Start everything
docker compose -f docker-compose-mac.yml up -d

# 3. Open http://localhost:8501
```

## Option B: Local PostgreSQL + Docker App
```bash
# 1. Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 2. Create database
createuser -s fusemachines
createdb adaptive_exam_db -O fusemachines
psql -d adaptive_exam_db -c "ALTER USER fusemachines PASSWORD 'your_strong_password';"

# 3. Import your data (if you have a dump)
# pg_restore -U fusemachines -d adaptive_exam_db --clean --if-exists your_dump.dump

# 4. Run app in Docker
docker compose -f docker-compose-external-mac.yml up -d

# 5. Open http://localhost:8501
```

## Option C: Use PostgreSQL.app (GUI)
1. Download PostgreSQL.app from https://postgresapp.com/
2. Install and start it
3. Use pgAdmin or similar to create database and import data
4. Run: docker compose -f docker-compose-external-mac.yml up -d

## Troubleshooting
- If you get connection errors, check if PostgreSQL is running: `brew services list | grep postgresql`
- For Docker connection issues, try using `localhost` instead of `host.docker.internal`
- Make sure Docker Desktop is running before starting containers
