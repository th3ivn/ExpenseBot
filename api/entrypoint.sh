#!/bin/sh
set -e

echo "Running database migrations..."
cd /app

# If tables already exist but alembic_version doesn't, stamp the initial migration
# This handles the case where tables were created outside of Alembic (e.g. by SQLAlchemy create_all)
python -c "
import os, sys
from sqlalchemy import create_engine, text

url = os.environ.get('DATABASE_URL', '')
if url.startswith('postgresql+asyncpg://'):
    url = url.replace('postgresql+asyncpg://', 'postgresql://', 1)
elif url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)

try:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text(
                \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')\"
            )).scalar()

            if not result:
                # Check if our app tables already exist
                tables_exist = conn.execute(text(
                    \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')\"
                )).scalar()

                if tables_exist:
                    print('Tables exist but alembic_version missing. Stamping 001_initial...')
                    conn.execute(text(
                        \"CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))\"
                    ))
                    conn.execute(text(
                        \"INSERT INTO alembic_version (version_num) VALUES ('001_initial')\"
                    ))
                    conn.commit()
                    print('Done. Alembic will skip initial migration.')
                else:
                    print('Fresh database. Alembic will run all migrations.')
            else:
                print('alembic_version exists. Normal migration flow.')
    finally:
        engine.dispose()
except Exception as e:
    print(f'Pre-migration check failed (non-fatal): {e}', file=sys.stderr)
"

alembic -c api/database/migrations/alembic.ini upgrade head

echo "Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
