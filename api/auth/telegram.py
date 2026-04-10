import hashlib
import hmac
import json
from urllib.parse import parse_qsl, unquote


def verify_init_data(init_data: str, bot_token: str) -> dict:
    """
    Validate Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user dict on success, raises ValueError on failure.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise ValueError("Hash відсутній у initData")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()

    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()  # type: ignore[attr-defined]

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Невірний підпис initData")

    user_str = params.get("user")
    if not user_str:
        raise ValueError("Дані користувача відсутні в initData")

    return json.loads(unquote(user_str))
