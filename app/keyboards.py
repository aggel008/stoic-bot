from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\U0001f4d6 Урок дня", callback_data="menu:lesson")],
        [InlineKeyboardButton(text="\U0001f52e Случайная мудрость", callback_data="menu:wisdom")],
        [InlineKeyboardButton(text="\U0001f4ca Статистика", callback_data="menu:stats")],
        [InlineKeyboardButton(text="\u2699\ufe0f Настройки", callback_data="menu:settings")],
    ])


def lesson_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u23ed Следующий урок", callback_data="lesson:next")],
        [InlineKeyboardButton(text="\u270d\ufe0f Записать размышления", callback_data="lesson:reflect")],
        [InlineKeyboardButton(text="\U0001f3e0 Меню", callback_data="lesson:back")],
    ])


def settings_kb(daily_enabled: bool) -> InlineKeyboardMarkup:
    if daily_enabled:
        toggle = InlineKeyboardButton(text="\U0001f515 Отключить рассылку", callback_data="settings:daily_off")
    else:
        toggle = InlineKeyboardButton(text="\U0001f514 Включить рассылку", callback_data="settings:daily_on")
    return InlineKeyboardMarkup(inline_keyboard=[
        [toggle],
        [InlineKeyboardButton(text="\U0001f512 Конфиденциальность", callback_data="settings:privacy")],
        [InlineKeyboardButton(text="\U0001f5d1 Удалить мои данные", callback_data="settings:delete")],
        [InlineKeyboardButton(text="\U0001f3e0 Меню", callback_data="settings:back")],
    ])


def daily_hour_kb() -> InlineKeyboardMarkup:
    rows = []
    for row_start in [5, 8]:
        row = [
            InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"daily:hour:{h:02d}")
            for h in range(row_start, row_start + 3)
        ]
        rows.append(row)
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="settings:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def daily_minute_kb(hour: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{hour}:00", callback_data=f"daily:min:{hour}:00"),
            InlineKeyboardButton(text=f"{hour}:30", callback_data=f"daily:min:{hour}:30"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="settings:daily_on")],
    ])


def reflection_skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="reflect:skip")],
    ])


def delete_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", callback_data="delete:confirm"),
            InlineKeyboardButton(text="Отмена", callback_data="delete:cancel"),
        ],
    ])


def evening_reflection_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u270d\ufe0f Записать ответы", callback_data="lesson:reflect")],
        [InlineKeyboardButton(text="\U0001f3e0 Меню", callback_data="lesson:back")],
    ])
