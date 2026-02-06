import os
import random
import ujson as json
from datetime import date, timedelta
from typing import Any, Dict, List


def _read(path: str, default: Any):
    if not os.path.exists(path):
        if os.path.dirname(path) and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError:
            return default


class _BaseStorage:
    def _write(self):
        if os.path.dirname(self.path) and not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        if os.path.exists(tmp):
            os.remove(tmp)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        if os.path.isdir(self.path):
            os.remove(self.path)
        os.replace(tmp, self.path)


# -------------------- LESSONS --------------------

class Lessons(_BaseStorage):
    def __init__(self, path: str):
        self.path = path
        self._data = _read(path, [])
        if not isinstance(self._data, list):
            self._data = []

    def by_id(self, lid: int) -> Dict:
        return next(x for x in self._data if x["id"] == lid)

    def max_id(self) -> int:
        return max(x["id"] for x in self._data) if self._data else 1

    def count(self) -> int:
        return len(self._data)

    def random_quote(self) -> Dict:
        return random.choice(self._data)


# -------------------- USERS --------------------

_USER_DEFAULTS = {
    "daily_enabled": False,
    "daily_time": "07:00",
    "next_lesson_id": 1,
    "waiting": None,
    "last_push_date": None,
    "last_afternoon_date": None,
    "last_evening_date": None,
    "last_activity": None,
    "streak": 0,
    "streak_last_date": None,
    "reflection_count": 0,
    "registered_at": None,
    "today_lesson_id": None,
    "nudge_sent_date": None,
}


class Users(_BaseStorage):
    def __init__(self, path: str):
        self.path = path
        self._data: Dict[str, Dict[str, Any]] = _read(path, {})

    def _save(self):
        self._write()

    def ensure(self, uid: int):
        key = str(uid)
        if key not in self._data:
            d = _USER_DEFAULTS.copy()
            d["registered_at"] = str(date.today())
            self._data[key] = d
            self._save()
        else:
            changed = False
            for k, v in _USER_DEFAULTS.items():
                if k not in self._data[key]:
                    self._data[key][k] = v
                    changed = True
            if changed:
                self._save()

    # --- lesson tracking ---

    def get_next_lesson(self, uid: int) -> int:
        self.ensure(uid)
        return int(self._data[str(uid)]["next_lesson_id"])

    def advance(self, uid: int, max_id: int) -> int:
        self.ensure(uid)
        cur = int(self._data[str(uid)]["next_lesson_id"])
        nxt = cur + 1 if cur < max_id else 1
        self._data[str(uid)]["next_lesson_id"] = nxt
        self._save()
        return nxt

    def set_today_lesson(self, uid: int, lesson_id: int):
        self.ensure(uid)
        self._data[str(uid)]["today_lesson_id"] = lesson_id
        self._save()

    def get_today_lesson(self, uid: int) -> int | None:
        self.ensure(uid)
        return self._data[str(uid)].get("today_lesson_id")

    # --- activity ---

    def touch_activity(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["last_activity"] = str(date.today())
        self._save()

    # --- daily push tracking ---

    def enable_daily(self, uid: int, time_str: str):
        self.ensure(uid)
        self._data[str(uid)]["daily_enabled"] = True
        self._data[str(uid)]["daily_time"] = time_str
        self._save()

    def disable_daily(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["daily_enabled"] = False
        self._save()

    def pushed_today(self, uid: int) -> bool:
        self.ensure(uid)
        return self._data[str(uid)].get("last_push_date") == str(date.today())

    def set_last_push_today(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["last_push_date"] = str(date.today())
        self._save()

    def pushed_afternoon(self, uid: int) -> bool:
        self.ensure(uid)
        return self._data[str(uid)].get("last_afternoon_date") == str(date.today())

    def set_afternoon_pushed(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["last_afternoon_date"] = str(date.today())
        self._save()

    def pushed_evening(self, uid: int) -> bool:
        self.ensure(uid)
        return self._data[str(uid)].get("last_evening_date") == str(date.today())

    def set_evening_pushed(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["last_evening_date"] = str(date.today())
        self._save()

    # --- streak & reflection ---

    def increment_streak(self, uid: int):
        self.ensure(uid)
        key = str(uid)
        today_str = str(date.today())
        yesterday_str = str(date.today() - timedelta(days=1))
        last = self._data[key].get("streak_last_date")
        if last == today_str:
            return
        if last == yesterday_str:
            self._data[key]["streak"] += 1
        else:
            self._data[key]["streak"] = 1
        self._data[key]["streak_last_date"] = today_str
        self._save()

    def increment_reflection_count(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["reflection_count"] = (
            self._data[str(uid)].get("reflection_count", 0) + 1
        )
        self._save()

    # --- stats ---

    def get_stats(self, uid: int) -> dict:
        self.ensure(uid)
        d = self._data[str(uid)]
        return {
            "streak": d.get("streak", 0),
            "reflection_count": d.get("reflection_count", 0),
            "registered_at": d.get("registered_at"),
            "daily_enabled": d.get("daily_enabled", False),
            "daily_time": d.get("daily_time", "07:00"),
            "current_lesson": d.get("next_lesson_id", 1),
        }

    # --- inactivity ---

    def get_inactive_users(self, threshold_days: int = 2) -> List[int]:
        result = []
        today = date.today()
        today_str = str(today)
        for uid_str, cfg in self._data.items():
            if not cfg.get("daily_enabled"):
                continue
            if cfg.get("nudge_sent_date") == today_str:
                continue
            last = cfg.get("last_activity")
            if last:
                delta = (today - date.fromisoformat(last)).days
                if delta >= threshold_days:
                    result.append(int(uid_str))
            else:
                result.append(int(uid_str))
        return result

    def set_nudge_sent(self, uid: int):
        self.ensure(uid)
        self._data[str(uid)]["nudge_sent_date"] = str(date.today())
        self._save()

    # --- waiting (legacy, kept for compat) ---

    def set_waiting(self, uid: int, what: str | None):
        self.ensure(uid)
        self._data[str(uid)]["waiting"] = what
        self._save()

    def get_waiting(self, uid: int) -> str | None:
        self.ensure(uid)
        return self._data[str(uid)].get("waiting")

    def clear_waiting(self, uid: int):
        self.set_waiting(uid, None)

    # --- delete ---

    def delete(self, uid: int):
        key = str(uid)
        if key in self._data:
            del self._data[key]
            self._save()


# -------------------- JOURNAL --------------------

class Journal(_BaseStorage):
    def __init__(self, path: str):
        self.path = path
        self._data: Dict[str, Any] = _read(path, {})

    def _save(self):
        self._write()

    def append(self, uid: int, lesson_id: int, answers: Dict[str, Any]):
        key = str(uid)
        self._data.setdefault(key, []).append({
            "date": str(date.today()),
            "lesson_id": lesson_id,
            "answers": answers,
        })
        self._save()

    def count(self, uid: int) -> int:
        return len(self._data.get(str(uid), []))

    def has_reflected_today(self, uid: int) -> bool:
        entries = self._data.get(str(uid), [])
        today_str = str(date.today())
        return any(e.get("date") == today_str for e in entries)

    def delete(self, uid: int):
        key = str(uid)
        if key in self._data:
            del self._data[key]
            self._save()
