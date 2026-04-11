"""Fix transactions schema — add missing columns/indexes to all tables

Revision ID: 002_fix_transactions_schema
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

This migration is idempotent: every ALTER TABLE uses ADD COLUMN IF NOT EXISTS
and every CREATE INDEX uses IF NOT EXISTS, so it is safe to run multiple times.
"""
from alembic import op

revision = "002_fix_transactions_schema"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Ensure ENUMs exist
    # ------------------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transaction_type') THEN
                CREATE TYPE transaction_type AS ENUM ('expense', 'income', 'transfer');
            END IF;
        END
        $$
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recurring_frequency') THEN
                CREATE TYPE recurring_frequency AS ENUM ('daily', 'weekly', 'monthly', 'yearly');
            END IF;
        END
        $$
    """)

    # ------------------------------------------------------------------
    # 2. users — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE users
            ADD COLUMN IF NOT EXISTS telegram_id BIGINT      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS first_name  VARCHAR(255) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS username    VARCHAR(255),
            ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_id_unique
            ON users (telegram_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users (telegram_id)
    """)

    # ------------------------------------------------------------------
    # 3. categories — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE categories
            ADD COLUMN IF NOT EXISTS user_id    INTEGER      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS name       VARCHAR(255) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS emoji      VARCHAR(16)  NOT NULL DEFAULT '📦',
            ADD COLUMN IF NOT EXISTS color      VARCHAR(16)  NOT NULL DEFAULT '#8E8E93',
            ADD COLUMN IF NOT EXISTS group_name VARCHAR(255),
            ADD COLUMN IF NOT EXISTS sort_order INTEGER      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP    NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_user_id ON categories (user_id)
    """)

    # ------------------------------------------------------------------
    # 4. accounts — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE accounts
            ADD COLUMN IF NOT EXISTS user_id         INTEGER        NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS name            VARCHAR(255)   NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS emoji           VARCHAR(16)    NOT NULL DEFAULT '💳',
            ADD COLUMN IF NOT EXISTS opening_balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS is_active       BOOLEAN        NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS sort_order      INTEGER        NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS created_at      TIMESTAMP      NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts (user_id)
    """)

    # ------------------------------------------------------------------
    # 5. transactions — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE transactions
            ADD COLUMN IF NOT EXISTS user_id       INTEGER          NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS type          transaction_type NOT NULL DEFAULT 'expense',
            ADD COLUMN IF NOT EXISTS amount        NUMERIC(12, 2)   NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS description   VARCHAR(1024),
            ADD COLUMN IF NOT EXISTS merchant      VARCHAR(255),
            ADD COLUMN IF NOT EXISTS category_id   INTEGER,
            ADD COLUMN IF NOT EXISTS account_id    INTEGER,
            ADD COLUMN IF NOT EXISTS to_account_id INTEGER,
            ADD COLUMN IF NOT EXISTS date          TIMESTAMP        NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS created_at    TIMESTAMP        NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at    TIMESTAMP        NOT NULL DEFAULT NOW()
    """)

    # Add FK constraints if they don't already exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'transactions'
                  AND constraint_name = 'transactions_category_id_fkey'
            ) THEN
                ALTER TABLE transactions
                    ADD CONSTRAINT transactions_category_id_fkey
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL;
            END IF;
        END
        $$
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'transactions'
                  AND constraint_name = 'transactions_account_id_fkey'
            ) THEN
                ALTER TABLE transactions
                    ADD CONSTRAINT transactions_account_id_fkey
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT;
            END IF;
        END
        $$
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'transactions'
                  AND constraint_name = 'transactions_to_account_id_fkey'
            ) THEN
                ALTER TABLE transactions
                    ADD CONSTRAINT transactions_to_account_id_fkey
                    FOREIGN KEY (to_account_id) REFERENCES accounts(id) ON DELETE RESTRICT;
            END IF;
        END
        $$
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_transactions_user_id     ON transactions (user_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_transactions_category_id ON transactions (category_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_transactions_account_id  ON transactions (account_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_transactions_date        ON transactions (date)
    """)

    # ------------------------------------------------------------------
    # 6. tags — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE tags
            ADD COLUMN IF NOT EXISTS user_id    INTEGER      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS name       VARCHAR(100) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS color      VARCHAR(16)  NOT NULL DEFAULT '#8E8E93',
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP    NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tags_user_id ON tags (user_id)
    """)

    # ------------------------------------------------------------------
    # 7. transaction_tags — create if missing, or add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'transaction_tags'
            ) THEN
                CREATE TABLE transaction_tags (
                    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
                    tag_id         INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (transaction_id, tag_id)
                );
            END IF;
        END
        $$
    """)

    # ------------------------------------------------------------------
    # 8. budgets — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE budgets
            ADD COLUMN IF NOT EXISTS user_id          INTEGER        NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS amount           NUMERIC(12, 2) NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS period_start_day INTEGER        NOT NULL DEFAULT 1,
            ADD COLUMN IF NOT EXISTS is_active        BOOLEAN        NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at       TIMESTAMP      NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_budgets_user_id ON budgets (user_id)
    """)

    # ------------------------------------------------------------------
    # 9. recurring_transactions — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE recurring_transactions
            ADD COLUMN IF NOT EXISTS user_id       INTEGER              NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS type          VARCHAR(16)          NOT NULL DEFAULT 'expense',
            ADD COLUMN IF NOT EXISTS amount        NUMERIC(12, 2)       NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS description   VARCHAR(1024),
            ADD COLUMN IF NOT EXISTS category_id   INTEGER,
            ADD COLUMN IF NOT EXISTS account_id    INTEGER,
            ADD COLUMN IF NOT EXISTS to_account_id INTEGER,
            ADD COLUMN IF NOT EXISTS frequency     recurring_frequency  NOT NULL DEFAULT 'monthly',
            ADD COLUMN IF NOT EXISTS next_date     TIMESTAMP            NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS is_active     BOOLEAN              NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at    TIMESTAMP            NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_recurring_transactions_user_id
            ON recurring_transactions (user_id)
    """)

    # ------------------------------------------------------------------
    # 10. merchant_rules — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE merchant_rules
            ADD COLUMN IF NOT EXISTS user_id          INTEGER      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS merchant_pattern VARCHAR(255) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS category_id      INTEGER      NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_merchant_rules_user_id ON merchant_rules (user_id)
    """)

    # ------------------------------------------------------------------
    # 11. user_settings — add missing columns
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE user_settings
            ADD COLUMN IF NOT EXISTS user_id                 INTEGER     NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS budget_period_start_day INTEGER     NOT NULL DEFAULT 1,
            ADD COLUMN IF NOT EXISTS theme                   VARCHAR(32) NOT NULL DEFAULT 'dark',
            ADD COLUMN IF NOT EXISTS created_at              TIMESTAMP   NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at              TIMESTAMP   NOT NULL DEFAULT NOW()
    """)


def downgrade() -> None:
    # This migration only adds columns/indexes — downgrade is a no-op because
    # dropping columns that may have been there from the start is destructive.
    pass
