import pytest

import bot.state as state


@pytest.fixture(autouse=True)
def clear_state():
    """Reset state before each test."""
    state._last_menu_message.clear()
    yield
    state._last_menu_message.clear()


def test_get_returns_none_when_not_set(user_id):
    assert state.get_last_menu_message(user_id) is None


def test_set_and_get(user_id, message_id):
    state.set_last_menu_message(user_id, message_id)
    assert state.get_last_menu_message(user_id) == message_id


def test_set_overwrites_existing(user_id):
    state.set_last_menu_message(user_id, 10)
    state.set_last_menu_message(user_id, 99)
    assert state.get_last_menu_message(user_id) == 99


def test_clear_removes_entry(user_id, message_id):
    state.set_last_menu_message(user_id, message_id)
    state.clear_last_menu_message(user_id)
    assert state.get_last_menu_message(user_id) is None


def test_clear_nonexistent_does_not_raise(user_id):
    state.clear_last_menu_message(user_id)  # should not raise


def test_multiple_users_isolated():
    state.set_last_menu_message(1, 100)
    state.set_last_menu_message(2, 200)
    assert state.get_last_menu_message(1) == 100
    assert state.get_last_menu_message(2) == 200
    state.clear_last_menu_message(1)
    assert state.get_last_menu_message(1) is None
    assert state.get_last_menu_message(2) == 200
