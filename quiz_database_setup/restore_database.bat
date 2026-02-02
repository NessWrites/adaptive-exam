@echo off
echo ================================================
echo Quiz Database Restore Script
echo ================================================
echo.
echo This will create the quiz_database and restore all data.
echo.
pause

set /p DB_USER="Enter PostgreSQL username (default: postgres): " 
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_HOST="Enter PostgreSQL host (default: localhost): "
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_PORT="Enter PostgreSQL port (default: 5432): "
if "%DB_PORT%"=="" set DB_PORT=5432

echo.
echo ================================================
echo Configuration:
echo   User: %DB_USER%
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: quiz_database
echo ================================================
echo.

echo Checking if database exists...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -lqt | findstr /C:"quiz_database" >nul
if %errorlevel% equ 0 (
    echo WARNING: Database 'quiz_database' already exists!
    set /p CONFIRM="Do you want to DROP and recreate it? (yes/no): "
    if /i "%CONFIRM%"=="yes" (
        echo Dropping existing database...
        psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -c "DROP DATABASE quiz_database;"
    ) else (
        echo Cancelled by user.
        pause
        exit /b
    )
)

echo Creating database...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE quiz_database;"

echo Restoring backup...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d quiz_database -f quiz_database_backup.sql

echo.
echo ================================================
echo Database restore complete!
echo ================================================
echo.
echo Database details:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: quiz_database
echo   Username: %DB_USER%
echo.
echo You can now connect your application to this database.
echo.
pause