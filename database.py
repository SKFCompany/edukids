"""
Локальная база данных (SQLite) — полностью офлайн.
Хранит: профили детей, монеты/опыт/уровень, прогресс по темам,
историю ответов (для аналитики родителю в будущем).
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "edukids.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    grade INTEGER NOT NULL DEFAULT 1,
    avatar TEXT DEFAULT 'cat',
    language TEXT DEFAULT 'ru',
    coins INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS owned_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    acquired_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    UNIQUE(profile_id, item_id)
);

CREATE TABLE IF NOT EXISTS topic_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    subject TEXT NOT NULL,          -- 'math' | 'reading'
    topic_id TEXT NOT NULL,         -- напр. 'math_g3_multiplication'
    tasks_completed INTEGER DEFAULT 0,
    tasks_total INTEGER DEFAULT 0,
    stars INTEGER DEFAULT 0,        -- 0-3, качество прохождения
    completed_at TEXT,
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    UNIQUE(profile_id, subject, topic_id)
);

CREATE TABLE IF NOT EXISTS answer_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    task_id TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    attempts INTEGER DEFAULT 1,
    answered_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    badge_id TEXT NOT NULL,
    earned_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    UNIQUE(profile_id, badge_id)
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        # Миграция для БД, созданных до появления новых полей.
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(profiles)").fetchall()]
        if "equipped_accessory" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN equipped_accessory TEXT DEFAULT NULL")
        if "equipped_room" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN equipped_room TEXT DEFAULT 'room_sky'")
        if "equipped_companion" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN equipped_companion TEXT DEFAULT 'comp_duck'")


# ---------- Профили ----------

def create_profile(name: str, grade: int, avatar: str = "cat", language: str = "ru") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO profiles (name, grade, avatar, language) VALUES (?, ?, ?, ?)",
            (name, grade, avatar, language),
        )
        return cur.lastrowid


def get_profile(profile_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        return dict(row) if row else None


def list_profiles():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM profiles ORDER BY id").fetchall()
        return [dict(r) for r in rows]


# ---------- Прогресс и геймификация ----------

def record_answer(profile_id: int, task_id: str, is_correct: bool):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO answer_log (profile_id, task_id, is_correct) VALUES (?, ?, ?)",
            (profile_id, task_id, int(is_correct)),
        )


def add_rewards(profile_id: int, coins: int = 0, xp: int = 0):
    """Начислить монеты и опыт, пересчитать уровень. Уровень растёт по формуле
    100 * level XP на переход — просто и предсказуемо для ребёнка."""
    with get_connection() as conn:
        profile = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        new_coins = profile["coins"] + coins
        new_xp = profile["xp"] + xp
        new_level = profile["level"]
        while new_xp >= new_level * 100:
            new_xp -= new_level * 100
            new_level += 1
        conn.execute(
            "UPDATE profiles SET coins = ?, xp = ?, level = ? WHERE id = ?",
            (new_coins, new_xp, new_level, profile_id),
        )
        return {"coins": new_coins, "xp": new_xp, "level": new_level, "leveled_up": new_level > profile["level"]}


def update_topic_progress(profile_id: int, subject: str, topic_id: str,
                           tasks_completed: int, tasks_total: int, stars: int):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO topic_progress (profile_id, subject, topic_id, tasks_completed, tasks_total, stars, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
               ON CONFLICT(profile_id, subject, topic_id)
               DO UPDATE SET tasks_completed=excluded.tasks_completed,
                              tasks_total=excluded.tasks_total,
                              stars=MAX(topic_progress.stars, excluded.stars),
                              completed_at=excluded.completed_at""",
            (profile_id, subject, topic_id, tasks_completed, tasks_total, stars),
        )


def get_subject_progress(profile_id: int, subject: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM topic_progress WHERE profile_id = ? AND subject = ?",
            (profile_id, subject),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- Магазин ----------

def get_owned_item_ids(profile_id: int) -> set:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT item_id FROM owned_items WHERE profile_id = ?", (profile_id,)
        ).fetchall()
        return {r["item_id"] for r in rows}


def purchase_item(profile_id: int, item_id: str, price: int) -> str:
    """Списывает монеты и выдаёт предмет. Возвращает 'ok' / 'already_owned' / 'not_enough_coins'."""
    with get_connection() as conn:
        profile = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        owned = conn.execute(
            "SELECT 1 FROM owned_items WHERE profile_id = ? AND item_id = ?", (profile_id, item_id)
        ).fetchone()
        if owned:
            return "already_owned"
        if profile["coins"] < price:
            return "not_enough_coins"
        conn.execute("UPDATE profiles SET coins = coins - ? WHERE id = ?", (price, profile_id))
        conn.execute("INSERT INTO owned_items (profile_id, item_id) VALUES (?, ?)", (profile_id, item_id))
        return "ok"


def equip_avatar(profile_id: int, item_id: str):
    with get_connection() as conn:
        conn.execute("UPDATE profiles SET avatar = ? WHERE id = ?", (item_id, profile_id))


def equip_accessory(profile_id: int, item_id: str):
    with get_connection() as conn:
        conn.execute("UPDATE profiles SET equipped_accessory = ? WHERE id = ?", (item_id, profile_id))


def unequip_accessory(profile_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE profiles SET equipped_accessory = NULL WHERE id = ?", (profile_id,))


def equip_room(profile_id: int, item_id: str):
    with get_connection() as conn:
        conn.execute("UPDATE profiles SET equipped_room = ? WHERE id = ?", (item_id, profile_id))


def update_grade(profile_id: int, grade: int):
    with get_connection() as conn:
        conn.execute("UPDATE profiles SET grade = ? WHERE id = ?", (grade, profile_id))


def grant_achievement(profile_id: int, badge_id: str) -> bool:
    """Возвращает True если значок выдан впервые."""
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO achievements (profile_id, badge_id) VALUES (?, ?)",
                (profile_id, badge_id),
            )
            return True
        except sqlite3.IntegrityError:
            return False  # уже был выдан раньше


if __name__ == "__main__":
    init_db()
    print(f"База данных готова: {DB_PATH}")
