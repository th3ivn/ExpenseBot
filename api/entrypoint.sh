#!/bin/sh
set -e

echo "Running database migrations..."
cd /app
alembic -c api/database/migrations/alembic.ini upgrade head

echo "Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
