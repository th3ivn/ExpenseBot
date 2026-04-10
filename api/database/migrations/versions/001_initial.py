"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE users (
            id          SERIAL PRIMARY KEY,
            telegram_id BIGINT      NOT NULL UNIQUE,
            first_name  VARCHAR(255) NOT NULL,
            username    VARCHAR(255),
            created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_users_telegram_id ON users (telegram_id)")

    op.execute("""
        CREATE TABLE categories (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name        VARCHAR(255) NOT NULL,
            emoji       VARCHAR(16)  NOT NULL DEFAULT '📦',
            color       VARCHAR(16)  NOT NULL DEFAULT '#8E8E93',
            group_name  VARCHAR(255),
            sort_order  INTEGER      NOT NULL DEFAULT 0,
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_categories_user_id ON categories (user_id)")

    op.execute("""
        CREATE TABLE accounts (
            id               SERIAL PRIMARY KEY,
            user_id          INTEGER        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name             VARCHAR(255)   NOT NULL,
            emoji            VARCHAR(16)    NOT NULL DEFAULT '💳',
            opening_balance  NUMERIC(12, 2) NOT NULL DEFAULT 0,
            is_active        BOOLEAN        NOT NULL DEFAULT TRUE,
            sort_order       INTEGER        NOT NULL DEFAULT 0,
            created_at       TIMESTAMP      NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_accounts_user_id ON accounts (user_id)")

    op.execute("""
        CREATE TYPE transaction_type AS ENUM ('expense', 'income', 'transfer')
    """)

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
    op.execute("CREATE INDEX ix_transactions_user_id ON transactions (user_id)")
    op.execute("CREATE INDEX ix_transactions_category_id ON transactions (category_id)")
    op.execute("CREATE INDEX ix_transactions_account_id ON transactions (account_id)")
    op.execute("CREATE INDEX ix_transactions_date ON transactions (date)")

    op.execute("""
        CREATE TABLE tags (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name       VARCHAR(100) NOT NULL,
            color      VARCHAR(16)  NOT NULL DEFAULT '#8E8E93',
            created_at TIMESTAMP   NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_tags_user_id ON tags (user_id)")

    op.execute("""
        CREATE TABLE transaction_tags (
            transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
            tag_id         INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (transaction_id, tag_id)
        )
    """)

    op.execute("""
        CREATE TABLE budgets (
            id                SERIAL PRIMARY KEY,
            user_id           INTEGER        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount            NUMERIC(12, 2) NOT NULL,
            period_start_day  INTEGER        NOT NULL DEFAULT 1,
            is_active         BOOLEAN        NOT NULL DEFAULT TRUE,
            created_at        TIMESTAMP      NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_budgets_user_id ON budgets (user_id)")

    op.execute("""
        CREATE TYPE recurring_frequency AS ENUM ('daily', 'weekly', 'monthly', 'yearly')
    """)

    op.execute("""
        CREATE TABLE recurring_transactions (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER              NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type          VARCHAR(16)          NOT NULL,
            amount        NUMERIC(12, 2)       NOT NULL,
            description   VARCHAR(1024),
            category_id   INTEGER              REFERENCES categories(id) ON DELETE SET NULL,
            account_id    INTEGER              NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
            to_account_id INTEGER              REFERENCES accounts(id) ON DELETE RESTRICT,
            frequency     recurring_frequency  NOT NULL,
            next_date     TIMESTAMP            NOT NULL,
            is_active     BOOLEAN              NOT NULL DEFAULT TRUE,
            created_at    TIMESTAMP            NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_recurring_transactions_user_id ON recurring_transactions (user_id)")

    op.execute("""
        CREATE TABLE merchant_rules (
            id               SERIAL PRIMARY KEY,
            user_id          INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            merchant_pattern VARCHAR(255) NOT NULL,
            category_id      INTEGER      NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX ix_merchant_rules_user_id ON merchant_rules (user_id)")

    op.execute("""
        CREATE TABLE user_settings (
            id                      SERIAL PRIMARY KEY,
            user_id                 INTEGER     NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            budget_period_start_day INTEGER     NOT NULL DEFAULT 1,
            theme                   VARCHAR(32) NOT NULL DEFAULT 'dark',
            created_at              TIMESTAMP   NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP   NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_settings")
    op.execute("DROP TABLE IF EXISTS merchant_rules")
    op.execute("DROP TABLE IF EXISTS recurring_transactions")
    op.execute("DROP TYPE IF EXISTS recurring_frequency")
    op.execute("DROP TABLE IF EXISTS budgets")
    op.execute("DROP TABLE IF EXISTS transaction_tags")
    op.execute("DROP TABLE IF EXISTS tags")
    op.execute("DROP TABLE IF EXISTS transactions")
    op.execute("DROP TYPE IF EXISTS transaction_type")
    op.execute("DROP TABLE IF EXISTS accounts")
    op.execute("DROP TABLE IF EXISTS categories")
    op.execute("DROP TABLE IF EXISTS users")
