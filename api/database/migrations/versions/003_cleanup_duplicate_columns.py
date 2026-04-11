"""Cleanup duplicate columns — drop and recreate transactions table cleanly

Revision ID: 003_cleanup_duplicate_columns
Revises: 002_fix_transactions_schema
Create Date: 2024-01-03 00:00:00.000000

The previous Base.metadata.create_all() call on startup created the
transactions table with SQLAlchemy auto-generated column names, while
Alembic migrations also added columns, resulting in duplicate/conflicting
columns (e.g. both `transaction_date` and `date`).

This migration drops the transactions and transaction_tags tables and
recreates them cleanly with the canonical schema from 001_initial.
The user has confirmed there is no important data to preserve.
"""
from alembic import op

revision = "003_cleanup_duplicate_columns"
down_revision = "002_fix_transactions_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop tables that may have duplicate/conflicting columns
    op.execute("DROP TABLE IF EXISTS transaction_tags CASCADE")
    op.execute("DROP TABLE IF EXISTS transactions CASCADE")

    # Recreate transactions with the canonical schema
    op.execute("""
        CREATE TABLE transactions (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type          transaction_type NOT NULL,
            amount        NUMERIC(12, 2)   NOT NULL,
            description   VARCHAR(1024),
            merchant      VARCHAR(255),
            category_id   INTEGER          REFERENCES categories(id) ON DELETE SET NULL,
            account_id    INTEGER          NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
            to_account_id INTEGER          REFERENCES accounts(id) ON DELETE RESTRICT,
            date          TIMESTAMP        NOT NULL,
            created_at    TIMESTAMP        NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMP        NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("CREATE INDEX ix_transactions_user_id     ON transactions (user_id)")
    op.execute("CREATE INDEX ix_transactions_category_id ON transactions (category_id)")
    op.execute("CREATE INDEX ix_transactions_account_id  ON transactions (account_id)")
    op.execute("CREATE INDEX ix_transactions_date        ON transactions (date)")

    # Recreate transaction_tags
    op.execute("""
        CREATE TABLE transaction_tags (
            transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
            tag_id         INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (transaction_id, tag_id)
        )
    """)


def downgrade() -> None:
    # This migration is intentionally irreversible: it performs a clean-slate
    # rebuild of tables that had duplicate/conflicting columns from a prior
    # Base.metadata.create_all() call.  Restoring the previous broken state
    # would not be useful, so the downgrade simply drops the recreated tables.
    op.execute("DROP TABLE IF EXISTS transaction_tags CASCADE")
    op.execute("DROP TABLE IF EXISTS transactions CASCADE")
