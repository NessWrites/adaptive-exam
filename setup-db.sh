#!/bin/bash
# Simple script to copy your local DB to Docker

echo "Creating database backup..."
mkdir -p backups
PGPASSWORD="your_password" pg_dump -h localhost -p 5432 -U fusemachines -d adaptive_exam_db -Fc -f backups/backup.dump

echo "Starting fresh PostgreSQL container..."
docker run --name temp_postgres -e POSTGRES_DB=adaptive_exam_db -e POSTGRES_USER=fusemachines -e POSTGRES_PASSWORD=your_strong_password -d postgres:15

echo "Waiting for PostgreSQL to start..."
sleep 10

echo "Restoring database..."
PGPASSWORD="your_strong_password" pg_restore -h localhost -p 5432 -U fusemachines -d adaptive_exam_db --clean --if-exists backups/backup.dump

echo "Creating volume from container..."
docker run --rm --volumes-from temp_postgres -v $(pwd):/backup ubuntu tar czf /backup/pgdata.tar.gz /var/lib/postgresql/data

echo "Cleaning up..."
docker stop temp_postgres
docker rm temp_postgres

echo "Done! Use docker-compose.yml to start with your data."
