import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from bot.webhook.server import _rate_limit, create_webhook_app

SECRET = "test-secret"
USER_ID = 111


@pytest.fixture(autouse=True)
def clear_rate_limit():
    _rate_limit.clear()
    yield
    _rate_limit.clear()


def _make_app() -> web.Application:
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    return create_webhook_app(bot=bot, allowed_user_id=USER_ID, webhook_secret=SECRET)


def _make_app_with_bot(bot) -> web.Application:
    return create_webhook_app(bot=bot, allowed_user_id=USER_ID, webhook_secret=SECRET)


async def _post(app: web.Application, data: dict, client_ip: str = "1.2.3.4"):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            json=data,
            headers={"X-Forwarded-For": client_ip},
        ) as resp:
            status = resp.status
            body = await resp.json()
    await runner.cleanup()
    return status, body


# ── Rate limiting ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    app = _make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    valid_payload = {
        "token": SECRET,
        "amount": 100.0,
        "merchant": "Silpo",
        "date": "2024-03-15T14:30:00",
    }

    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Send 10 requests (the limit)
        for _ in range(10):
            async with session.post(
                f"http://127.0.0.1:{port}/api/transaction",
                json=valid_payload,
            ) as resp:
                pass  # these may succeed or fail DB, but no rate limit yet

        # 11th request should be rate limited
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            json=valid_payload,
        ) as resp:
            assert resp.status == 429

    await runner.cleanup()


# ── Invalid JSON ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_json():
    app = _make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            data="not json",
            headers={"Content-Type": "application/json"},
        ) as resp:
            assert resp.status == 400
            body = await resp.json()
            assert "Invalid JSON" in body["error"]

    await runner.cleanup()


# ── Invalid token ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_token():
    app = _make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            json={"token": "wrong", "amount": 10, "merchant": "X", "date": "2024-01-01T00:00:00"},
        ) as resp:
            assert resp.status == 401

    await runner.cleanup()


# ── Negative amount ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_negative_amount():
    app = _make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            json={"token": SECRET, "amount": -50.0, "merchant": "X", "date": "2024-01-01T00:00:00"},
        ) as resp:
            assert resp.status == 400
            body = await resp.json()
            assert "positive" in body["error"].lower()

    await runner.cleanup()


# ── Empty merchant ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_empty_merchant():
    app = _make_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{port}/api/transaction",
            json={"token": SECRET, "amount": 10.0, "merchant": "   ", "date": "2024-01-01T00:00:00"},
        ) as resp:
            assert resp.status == 400
            body = await resp.json()
            assert "merchant" in body["error"].lower()

    await runner.cleanup()


# ── Successful transaction ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_successful_transaction():
    bot = AsyncMock()
    bot.send_message = AsyncMock()

    with patch("bot.webhook.server.save_transaction", new=AsyncMock(return_value=1)) as mock_save:
        app = _make_app_with_bot(bot)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://127.0.0.1:{port}/api/transaction",
                json={
                    "token": SECRET,
                    "amount": 150.0,
                    "merchant": "Silpo",
                    "date": "2024-03-15T14:30:00",
                },
            ) as resp:
                assert resp.status == 200
                body = await resp.json()
                assert body["ok"] is True
                assert body["id"] == 1

        mock_save.assert_called_once()
        bot.send_message.assert_called_once()

        await runner.cleanup()
