#!/bin/bash

echo "================================================"
echo "Quiz Database Restore Script"
echo "================================================"
echo
echo "This will create the quiz_database and restore all data."
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -p "Enter PostgreSQL host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter PostgreSQL port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

echo
echo "================================================"
echo "Configuration:"
echo "  User: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: quiz_database"
echo "================================================"
echo

echo "Checking if database exists..."
if psql -U $DB_USER -h $DB_HOST -p $DB_PORT -lqt | grep -qw quiz_database; then
    echo "WARNING: Database 'quiz_database' already exists!"
    read -p "Do you want to DROP and recreate it? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        echo "Dropping existing database..."
        psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "DROP DATABASE quiz_database;"
    else
        echo "Cancelled by user."
        exit 1
    fi
fi

echo "Creating database..."
psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE quiz_database;"

echo "Restoring backup..."
psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d quiz_database -f quiz_database_backup.sql

echo
echo "================================================"
echo "Database restore complete!"
echo "================================================"
echo
echo "Database details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: quiz_database"
echo "  Username: $DB_USER"
echo
echo "You can now connect your application to this database."
echo