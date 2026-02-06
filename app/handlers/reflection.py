from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.states import ReflectionFSM
from app.keyboards import reflection_skip_kb, main_menu_kb

router = Router()


@router.callback_query(F.data == "lesson:reflect")
async def cb_start_reflection(callback: types.CallbackQuery, state: FSMContext, users, lessons):
    uid = callback.from_user.id
    users.touch_activity(uid)
    today_lid = users.get_today_lesson(uid)
    if today_lid is None:
        today_lid = users.get_next_lesson(uid)
    lesson = lessons.by_id(today_lid)
    questions = lesson.get("reflection_questions", [])
    if not questions:
        await callback.answer("Для этого урока нет вопросов.", show_alert=True)
        return

    await state.set_state(ReflectionFSM.question_1)
    await state.update_data(lesson_id=today_lid, questions=questions, answers=[])

    await callback.message.answer(
        f"\U0001f4dd <b>Размышление по уроку {today_lid}</b>\n\n"
        f"Вопрос 1: <i>{questions[0]}</i>\n\n"
        f"Напиши свой ответ:",
        reply_markup=reflection_skip_kb(),
    )
    await callback.answer()


@router.message(ReflectionFSM.question_1)
async def fsm_answer_1(message: types.Message, state: FSMContext, users):
    uid = message.from_user.id
    users.touch_activity(uid)
    data = await state.get_data()
    questions = data["questions"]
    answers = data["answers"]
    answers.append(message.text)
    await state.update_data(answers=answers)

    if len(questions) > 1:
        await state.set_state(ReflectionFSM.question_2)
        await message.answer(
            f"Вопрос 2: <i>{questions[1]}</i>\n\n"
            f"Напиши свой ответ:",
            reply_markup=reflection_skip_kb(),
        )
    else:
        await _save_reflection(message, state, users)


@router.message(ReflectionFSM.question_2)
async def fsm_answer_2(message: types.Message, state: FSMContext, users, journal):
    uid = message.from_user.id
    users.touch_activity(uid)
    data = await state.get_data()
    data["answers"].append(message.text)
    await state.update_data(answers=data["answers"])
    await _save_reflection(message, state, users, journal)


async def _save_reflection(message: types.Message, state: FSMContext, users, journal=None):
    uid = message.from_user.id
    data = await state.get_data()
    lesson_id = data["lesson_id"]
    questions = data["questions"]
    answers = data["answers"]

    answers_dict = {}
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        answers_dict[f"q{i}"] = q
        answers_dict[f"a{i}"] = a

    if journal is not None:
        journal.append(uid, lesson_id, answers_dict)
    users.increment_reflection_count(uid)
    users.increment_streak(uid)

    streak = users.get_stats(uid)["streak"]
    await state.clear()
    await message.answer(
        f"\u2705 Записано! Твоя серия: <b>{streak}</b> дн.\n\n"
        f"Хорошая работа. Продолжай наблюдать.",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "reflect:skip")
async def cb_skip_reflection(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Размышление пропущено. Ты можешь вернуться к нему позже.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
