from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.routers import (
    auth,
    transactions,
    categories,
    accounts,
    budgets,
    tags,
    recurring,
    stats,
    settings as settings_router,
    webhook,
    merchant_rules,
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="ExpenseBot API",
    description="Production-grade expense tracking API for Telegram Mini App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(transactions.router, prefix=API_PREFIX)
app.include_router(categories.router, prefix=API_PREFIX)
app.include_router(accounts.router, prefix=API_PREFIX)
app.include_router(budgets.router, prefix=API_PREFIX)
app.include_router(tags.router, prefix=API_PREFIX)
app.include_router(recurring.router, prefix=API_PREFIX)
app.include_router(stats.router, prefix=API_PREFIX)
app.include_router(settings_router.router, prefix=API_PREFIX)
app.include_router(webhook.router, prefix=API_PREFIX)
app.include_router(merchant_rules.router, prefix=API_PREFIX)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/debug/schema", tags=["debug"])
async def debug_schema():
    """Temporary diagnostic endpoint — shows current DB schema for transactions.

    This endpoint is intentionally unauthenticated so the schema can be
    inspected directly from a browser.  Remove it once the schema issue
    is confirmed to be resolved.
    """
    from api.database.session import engine
    from sqlalchemy import text
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = 'transactions' "
            "ORDER BY ordinal_position"
        ))
        columns = [dict(row._mapping) for row in result.all()]

        tables_result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        ))
        tables = [row[0] for row in tables_result.all()]

    return {"transactions_columns": columns, "tables": tables}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
