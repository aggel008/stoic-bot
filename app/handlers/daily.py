from aiogram import Router, types, F

from app.keyboards import daily_hour_kb, daily_minute_kb, main_menu_kb

router = Router()


@router.callback_query(F.data == "settings:daily_on")
async def cb_daily_on(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выбери час утреннего урока:",
        reply_markup=daily_hour_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("daily:hour:"))
async def cb_pick_hour(callback: types.CallbackQuery):
    hour = callback.data.split(":")[2]
    await callback.message.edit_text(
        "Выбери минуты:",
        reply_markup=daily_minute_kb(hour),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("daily:min:"))
async def cb_pick_minute(callback: types.CallbackQuery, users):
    parts = callback.data.split(":")
    time_str = f"{parts[2]}:{parts[3]}"
    uid = callback.from_user.id
    users.enable_daily(uid, time_str)
    users.touch_activity(uid)
    await callback.message.edit_text(
        f"\U0001f514 Рассылка включена!\n\n"
        f"\U0001f555 Утренний урок: <b>{time_str}</b>\n"
        f"\U0001f550 Дневное напоминание: <b>14:00</b>\n"
        f"\U0001f319 Вечернее размышление: <b>21:00</b>",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:daily_off")
async def cb_daily_off(callback: types.CallbackQuery, users):
    uid = callback.from_user.id
    users.disable_daily(uid)
    users.touch_activity(uid)
    await callback.message.edit_text(
        "\U0001f515 Рассылка отключена.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
