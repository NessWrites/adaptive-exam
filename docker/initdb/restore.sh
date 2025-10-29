#!/bin/bash
set -euo pipefail

# This script runs inside the Postgres container during first initialization.
# It restores the database from /docker-entrypoint-initdb.d/seed.dump

DUMP_FILE="/docker-entrypoint-initdb.d/seed.dump"
DB_NAME="${POSTGRES_DB:-adaptive_exam_db}"
DB_USER="${POSTGRES_USER:-fusemachines}"

if [ -f "$DUMP_FILE" ]; then
  echo "[initdb] Restoring database '$DB_NAME' from $DUMP_FILE"
  pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists "$DUMP_FILE"
  echo "[initdb] Restore completed."
else
  echo "[initdb] No seed.dump found at $DUMP_FILE; skipping restore."
fi
