import pytest


@pytest.fixture
def user_id() -> int:
    return 123456789


@pytest.fixture
def chat_id() -> int:
    return 123456789


@pytest.fixture
def message_id() -> int:
    return 42
