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

app = FastAPI(
    title="ExpenseBot API",
    description="Production-grade expense tracking API for Telegram Mini App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
