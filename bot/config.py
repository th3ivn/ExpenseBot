import os
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str
    webhook_secret: str
    allowed_user_id: int
    webhook_host: str
    webhook_port: int
    api_base_url: str
    webapp_url: str


def load_config() -> Config:
    bot_token = os.environ["BOT_TOKEN"]
    webhook_secret = os.environ["WEBHOOK_SECRET"]
    allowed_user_id = int(os.environ["ALLOWED_USER_ID"])
    webhook_host = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
    webhook_port = int(os.environ.get("WEBHOOK_PORT", "8080"))
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    webapp_url = os.environ.get("WEBAPP_URL", "")

    return Config(
        bot_token=bot_token,
        webhook_secret=webhook_secret,
        allowed_user_id=allowed_user_id,
        webhook_host=webhook_host,
        webhook_port=webhook_port,
        api_base_url=api_base_url,
        webapp_url=webapp_url,
    )
