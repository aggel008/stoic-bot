from aiogram.fsm.state import StatesGroup, State


class ReflectionFSM(StatesGroup):
    question_1 = State()
    question_2 = State()
