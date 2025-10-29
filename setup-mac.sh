# MacBook setup instructions using Homebrew

# 1. Install PostgreSQL via Homebrew
brew install postgresql@15

# 2. Start PostgreSQL service
brew services start postgresql@15

# 3. Create database and user
createuser -s fusemachines
createdb adaptive_exam_db -O fusemachines

# 4. Set password for user
psql -d adaptive_exam_db -c "ALTER USER fusemachines PASSWORD 'your_strong_password';"

# 5. Import your database dump (if you have one)
# pg_restore -U fusemachines -d adaptive_exam_db --clean --if-exists path/to/your/dump.dump

# 6. Run only the app in Docker (connect to local PostgreSQL)
docker compose -f docker-compose-external-mac.yml up -d
