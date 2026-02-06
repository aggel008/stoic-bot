from aiogram import Router, types, F

from app.keyboards import lesson_kb, main_menu_kb
from app.formatting import render_lesson
from app.wisdom import get_random_wisdom

router = Router()


@router.callback_query(F.data == "menu:lesson")
async def cb_show_lesson(callback: types.CallbackQuery, users, lessons):
    uid = callback.from_user.id
    users.ensure(uid)
    users.touch_activity(uid)
    lid = users.get_next_lesson(uid)
    lesson = lessons.by_id(lid)
    users.set_today_lesson(uid, lid)
    text = render_lesson(lesson)
    await callback.message.edit_text(text, reply_markup=lesson_kb())
    await callback.answer()


@router.callback_query(F.data == "lesson:next")
async def cb_next_lesson(callback: types.CallbackQuery, users, lessons):
    uid = callback.from_user.id
    users.touch_activity(uid)
    users.advance(uid, lessons.max_id())
    lid = users.get_next_lesson(uid)
    lesson = lessons.by_id(lid)
    users.set_today_lesson(uid, lid)
    text = render_lesson(lesson)
    await callback.message.edit_text(text, reply_markup=lesson_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:wisdom")
async def cb_random_wisdom(callback: types.CallbackQuery, users):
    uid = callback.from_user.id
    users.touch_activity(uid)
    w = get_random_wisdom()
    text = f"\U0001f52e <b>{w['author']}</b>\n\n<i>\u00ab{w['quote']}\u00bb</i>"
    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()
