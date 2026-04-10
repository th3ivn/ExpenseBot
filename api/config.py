from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/expensebot"
    BOT_TOKEN: str = ""
    WEBHOOK_SECRET: str = ""
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
