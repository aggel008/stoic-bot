import logging
import random
from datetime import datetime, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from app.formatting import render_lesson, render_afternoon_reminder, render_evening_reflection
from app.keyboards import lesson_kb, evening_reflection_kb, main_menu_kb

log = logging.getLogger(__name__)


def setup_scheduler(bot, users, lessons):
    tz = ZoneInfo("Europe/Amsterdam")
    sched = AsyncIOScheduler(timezone=tz)

    async def morning_push():
        now_t = datetime.now(tz).time()
        for uid_str, cfg in list(users._data.items()):
            if not cfg.get("daily_enabled"):
                continue
            hh, mm = cfg.get("daily_time", "07:00").split(":")
            target = time(int(hh), int(mm))
            if now_t.hour != target.hour or now_t.minute != target.minute:
                continue
            uid = int(uid_str)
            if users.pushed_today(uid):
                continue
            lid = users.get_next_lesson(uid)
            lesson = lessons.by_id(lid)
            users.set_today_lesson(uid, lid)
            try:
                await bot.send_message(uid, render_lesson(lesson), reply_markup=lesson_kb())
            except Exception as e:
                log.warning("Morning push failed for %s: %s", uid, e)
                continue
            users.set_last_push_today(uid)
            users.advance(uid, lessons.max_id())

    async def afternoon_push():
        now_t = datetime.now(tz).time()
        if now_t.hour != 14 or now_t.minute != 0:
            return
        for uid_str, cfg in list(users._data.items()):
            if not cfg.get("daily_enabled"):
                continue
            uid = int(uid_str)
            if users.pushed_afternoon(uid):
                continue
            today_lid = users.get_today_lesson(uid)
            if today_lid is None:
                continue
            lesson = lessons.by_id(today_lid)
            try:
                await bot.send_message(uid, render_afternoon_reminder(lesson))
            except Exception as e:
                log.warning("Afternoon push failed for %s: %s", uid, e)
                continue
            users.set_afternoon_pushed(uid)

    async def evening_push():
        now_t = datetime.now(tz).time()
        if now_t.hour != 21 or now_t.minute != 0:
            return
        for uid_str, cfg in list(users._data.items()):
            if not cfg.get("daily_enabled"):
                continue
            uid = int(uid_str)
            if users.pushed_evening(uid):
                continue
            today_lid = users.get_today_lesson(uid)
            if today_lid is None:
                continue
            lesson = lessons.by_id(today_lid)
            try:
                await bot.send_message(
                    uid, render_evening_reflection(lesson), reply_markup=evening_reflection_kb()
                )
            except Exception as e:
                log.warning("Evening push failed for %s: %s", uid, e)
                continue
            users.set_evening_pushed(uid)

    async def inactivity_check():
        now_t = datetime.now(tz).time()
        if now_t.hour != 12 or now_t.minute != 0:
            return
        nudge_quotes = [
            "Помни: каждый день \u2014 это возможность стать лучше. \u2014 Марк Аврелий",
            "Не откладывай на завтра то, что может сделать тебя мудрее сегодня. \u2014 Сенека",
            "Препятствие на пути становится путём. \u2014 Марк Аврелий",
        ]
        for uid in users.get_inactive_users(threshold_days=2):
            try:
                await bot.send_message(
                    uid,
                    f"Давно тебя не было. Вот мысль на сегодня:\n\n"
                    f"<i>\u00ab{random.choice(nudge_quotes)}\u00bb</i>",
                    reply_markup=main_menu_kb(),
                )
            except Exception as e:
                log.warning("Nudge failed for %s: %s", uid, e)
                continue
            users.set_nudge_sent(uid)

    sched.add_job(morning_push, "interval", seconds=60, id="morning_tick")
    sched.add_job(afternoon_push, "interval", seconds=60, id="afternoon_tick")
    sched.add_job(evening_push, "interval", seconds=60, id="evening_tick")
    sched.add_job(inactivity_check, "interval", seconds=60, id="inactivity_tick")
    sched.start()
    return sched
