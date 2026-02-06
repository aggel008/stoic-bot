from typing import Dict, List


def render_lesson(ls: Dict) -> str:
    head = f"\U0001f4d6 <b>Урок {ls['id']}. {ls['title']}</b>\n"
    author = f"<i>{ls['author']}</i>\n\n"
    quote = f"\u00ab{ls['quote']}\u00bb\n\n"
    body = "\n".join(ls.get("body", [])) + "\n\n"
    practice = f"\U0001f3af <b>Практика:</b>\n{ls.get('practice', '')}\n\n"
    qs_list: List[str] = ls.get("reflection_questions", [])
    qs = "\U0001f4ad <b>Вопросы для размышления:</b>"
    for i, q in enumerate(qs_list, 1):
        qs += f"\n{i}) {q}"
    return head + author + quote + body + practice + qs


def render_afternoon_reminder(ls: Dict) -> str:
    return (
        f"\U0001f550 <b>Дневное напоминание</b>\n\n"
        f"Сегодня ты изучал: <b>{ls['title']}</b>\n\n"
        f"Напоминание: <i>{ls.get('practice', '')}</i>\n\n"
        f"Наблюдай. Замечай. Практикуй."
    )


def render_evening_reflection(ls: Dict) -> str:
    qs_list: List[str] = ls.get("reflection_questions", [])
    qs = ""
    for i, q in enumerate(qs_list, 1):
        qs += f"\n{i}) {q}"
    return (
        f"\U0001f319 <b>Вечернее размышление</b>\n\n"
        f"Сегодня ты работал над темой: <b>{ls['title']}</b>\n\n"
        f"Подумай:{qs}\n\n"
        f"Нажми кнопку ниже, чтобы записать свои мысли."
    )
