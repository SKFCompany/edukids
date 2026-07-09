"""
Загрузка тем и заданий по предмету/классу из локальных JSON-файлов.
Позже сюда так же просто добавляются новые предметы: kz_tili.json,
world_around.json, english.json — без изменения логики приложения.
"""

import json
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

_cache = {}


def _load_subject_file(subject: str) -> dict:
    if subject in _cache:
        return _cache[subject]
    path = os.path.join(CONTENT_DIR, f"{subject}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[subject] = data
    return data


def get_topics(subject: str, grade: int) -> list:
    """Список тем по предмету и классу."""
    data = _load_subject_file(subject)
    grade_data = data.get("grades", {}).get(str(grade))
    if not grade_data:
        return []
    return grade_data["topics"]


def get_topic(subject: str, grade: int, topic_id: str) -> dict | None:
    for topic in get_topics(subject, grade):
        if topic["topic_id"] == topic_id:
            return topic
    return None


def get_shop_catalog() -> dict:
    """Возвращает {'avatars': [...], 'accessories': [...]} из content/shop.json.
    Файл не содержит 'grades', поэтому кэшируется отдельно от предметов."""
    if "__shop__" in _cache:
        return _cache["__shop__"]
    path = os.path.join(CONTENT_DIR, "shop.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache["__shop__"] = data
    return data


def available_subjects() -> list:
    return [f.replace(".json", "") for f in os.listdir(CONTENT_DIR)
            if f.endswith(".json") and f != "shop.json"]
