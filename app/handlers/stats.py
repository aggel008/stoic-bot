from aiogram import Router, types, F

from app.keyboards import main_menu_kb

router = Router()


@router.callback_query(F.data == "menu:stats")
async def cb_stats(callback: types.CallbackQuery, users, lessons):
    uid = callback.from_user.id
    users.touch_activity(uid)
    s = users.get_stats(uid)
    total = lessons.count()
    reg = s['registered_at'] or "\u2014"
    daily_status = f"вкл ({s['daily_time']})" if s['daily_enabled'] else "выкл"
    text = (
        f"\U0001f4ca <b>Твоя статистика</b>\n\n"
        f"\U0001f525 Серия: <b>{s['streak']}</b> дн.\n"
        f"\U0001f4dd Размышлений: <b>{s['reflection_count']}</b>\n"
        f"\U0001f4d6 Текущий урок: <b>{s['current_lesson']}</b> из {total}\n"
        f"\U0001f4c5 Зарегистрирован: {reg}\n"
        f"\U0001f514 Рассылка: {daily_status}"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()
