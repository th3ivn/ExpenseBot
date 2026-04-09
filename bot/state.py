_last_menu_message: dict[int, int] = {}  # user_id -> message_id


def get_last_menu_message(user_id: int) -> int | None:
    return _last_menu_message.get(user_id)


def set_last_menu_message(user_id: int, message_id: int) -> None:
    _last_menu_message[user_id] = message_id


def clear_last_menu_message(user_id: int) -> None:
    _last_menu_message.pop(user_id, None)
