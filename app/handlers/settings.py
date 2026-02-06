from aiogram import Router, types, F

from app.keyboards import settings_kb, delete_confirm_kb, main_menu_kb
from app.texts import PRIVACY_TEXT

router = Router()


@router.callback_query(F.data == "menu:settings")
async def cb_settings(callback: types.CallbackQuery, users):
    uid = callback.from_user.id
    users.touch_activity(uid)
    d = users._data.get(str(uid), {})
    daily_on = d.get("daily_enabled", False)
    await callback.message.edit_text("\u2699\ufe0f Настройки:", reply_markup=settings_kb(daily_on))
    await callback.answer()


@router.callback_query(F.data == "settings:privacy")
async def cb_privacy(callback: types.CallbackQuery):
    await callback.message.edit_text(PRIVACY_TEXT, reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "settings:delete")
async def cb_delete_prompt(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "\u26a0\ufe0f Ты уверен? Это удалит все твои данные и записи безвозвратно.",
        reply_markup=delete_confirm_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "delete:confirm")
async def cb_delete_confirm(callback: types.CallbackQuery, users, journal):
    uid = callback.from_user.id
    users.delete(uid)
    journal.delete(uid)
    await callback.message.edit_text(
        "Все данные удалены. Чтобы начать заново, нажми /start.",
    )
    await callback.answer()
