#!/bin/sh
set -e

echo "Running database migrations..."
cd /app

# Use alembic stamp to mark migrations as done if tables already exist
# First, try to get current alembic version
CURRENT=$(alembic -c api/database/migrations/alembic.ini current 2>&1 || true)

if echo "$CURRENT" | grep -qE '(^|\s)001_initial(\s|$|\()'; then
    echo "Migration 001_initial already applied."
    alembic -c api/database/migrations/alembic.ini upgrade head
else
    ALEMBIC_ERR=$(mktemp)
    # Try upgrade, if it fails due to existing tables, stamp instead
    if ! alembic -c api/database/migrations/alembic.ini upgrade head 2>"$ALEMBIC_ERR"; then
        if grep -qE "relation .* already exists|already exists" "$ALEMBIC_ERR"; then
            echo "Tables already exist. Stamping current migration state..."
            alembic -c api/database/migrations/alembic.ini stamp head
            echo "Stamped. Future migrations will work normally."
        else
            echo "Migration failed with unexpected error:"
            cat "$ALEMBIC_ERR"
            rm -f "$ALEMBIC_ERR"
            exit 1
        fi
    fi
    rm -f "$ALEMBIC_ERR"
fi

echo "Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
