from aiogram import Router, types, F
from aiogram.filters import CommandStart

from app.keyboards import main_menu_kb
from app.texts import START_TEXT

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, users):
    users.ensure(message.from_user.id)
    users.touch_activity(message.from_user.id)
    await message.answer(START_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data.in_({"lesson:back", "settings:back", "delete:cancel"}))
async def cb_back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await callback.answer()
