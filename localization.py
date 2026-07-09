"""
Локализация интерфейса: русский / қазақша / english.
Использование:
    from localization import tr, set_language
    set_language("kk")
    label.text = tr("home_greeting")
"""

STRINGS = {
    "app_name": {
        "ru": "УмБала",
        "kk": "УмБала",
        "en": "UmBala",
    },
    "home_greeting": {
        "ru": "Привет, {name}!",
        "kk": "Сәлем, {name}!",
        "en": "Hi, {name}!",
    },
    "level": {
        "ru": "Уровень",
        "kk": "Деңгей",
        "en": "Level",
    },
    "todays_quest": {
        "ru": "Сегодняшний квест",
        "kk": "Бүгінгі квест",
        "en": "Today's quest",
    },
    "subjects": {
        "ru": "Предметы",
        "kk": "Пәндер",
        "en": "Subjects",
    },
    "subject_math": {
        "ru": "Математика",
        "kk": "Математика",
        "en": "Math",
    },
    "subject_reading": {
        "ru": "Чтение",
        "kk": "Оқу",
        "en": "Reading",
    },
    "subject_kazakh": {
        "ru": "Қазақ тілі",
        "kk": "Қазақ тілі",
        "en": "Kazakh",
    },
    "subject_english": {
        "ru": "Английский",
        "kk": "Ағылшын тілі",
        "en": "English",
    },
    "subject_world": {
        "ru": "Познание мира",
        "kk": "Дүниетану",
        "en": "World Knowledge",
    },
    "subject_world_science": {
        "ru": "Естествознание",
        "kk": "Жаратылыстану",
        "en": "Natural Science",
    },
    "grade": {
        "ru": "Класс",
        "kk": "Сынып",
        "en": "Grade",
    },
    "level_word": {
        "ru": "Уровень",
        "kk": "Деңгей",
        "en": "Level",
    },
    "locked_hint": {
        "ru": "Пройди прошлый уровень",
        "kk": "Алдыңғы деңгейден өт",
        "en": "Complete previous level",
    },
    "no_topics_yet": {
        "ru": "Темы для этого класса скоро появятся!",
        "kk": "Бұл сынып үшін тақырыптар жақында қосылады!",
        "en": "Topics for this grade are coming soon!",
    },
    "start": {
        "ru": "Начать",
        "kk": "Бастау",
        "en": "Start",
    },
    "continue": {
        "ru": "Продолжить",
        "kk": "Жалғастыру",
        "en": "Continue",
    },
    "check_answer": {
        "ru": "Проверить",
        "kk": "Тексеру",
        "en": "Check",
    },
    "correct": {
        "ru": "Правильно! Молодец!",
        "kk": "Дұрыс! Жарайсың!",
        "en": "Correct! Well done!",
    },
    "try_again": {
        "ru": "Почти! Попробуй ещё раз",
        "kk": "Жақын! Тағы бір рет көр",
        "en": "Almost! Try again",
    },
    "coins_earned": {
        "ru": "+{amount} монет",
        "kk": "+{amount} тиын",
        "en": "+{amount} coins",
    },
    "profile": {
        "ru": "Профиль",
        "kk": "Профиль",
        "en": "Profile",
    },
    "settings": {
        "ru": "Настройки",
        "kk": "Баптаулар",
        "en": "Settings",
    },
    "achievements": {
        "ru": "Достижения",
        "kk": "Жетістіктер",
        "en": "Achievements",
    },
    "language": {
        "ru": "Язык",
        "kk": "Тіл",
        "en": "Language",
    },
    "topics": {
        "ru": "Темы",
        "kk": "Тақырыптар",
        "en": "Topics",
    },
    "task_of": {
        "ru": "Задание {current} из {total}",
        "kk": "{current}/{total} тапсырма",
        "en": "Task {current} of {total}",
    },
    "shop": {
        "ru": "Магазин",
        "kk": "Дүкен",
        "en": "Shop",
    },
    "inventory": {
        "ru": "Инвентарь",
        "kk": "Мүлік",
        "en": "Inventory",
    },
    "rooms": {
        "ru": "Комнаты",
        "kk": "Бөлмелер",
        "en": "Rooms",
    },
    "avatars": {
        "ru": "Аватары",
        "kk": "Аватарлар",
        "en": "Avatars",
    },
    "accessories": {
        "ru": "Аксессуары",
        "kk": "Аксессуарлар",
        "en": "Accessories",
    },
    "buy": {
        "ru": "Купить",
        "kk": "Сатып алу",
        "en": "Buy",
    },
    "equip": {
        "ru": "Надеть",
        "kk": "Тағу",
        "en": "Equip",
    },
    "unequip": {
        "ru": "Снять",
        "kk": "Шешу",
        "en": "Remove",
    },
    "equipped": {
        "ru": "Надето",
        "kk": "Кигізілген",
        "en": "Equipped",
    },
    "not_enough_coins": {
        "ru": "Не хватает монет",
        "kk": "Тиын жеткіліксіз",
        "en": "Not enough coins",
    },
    "free": {
        "ru": "Бесплатно",
        "kk": "Тегін",
        "en": "Free",
    },
}

_current_language = "ru"
SUPPORTED_LANGUAGES = ("ru", "kk", "en")


def set_language(lang_code: str) -> None:
    global _current_language
    if lang_code in SUPPORTED_LANGUAGES:
        _current_language = lang_code
    else:
        raise ValueError(f"Unsupported language: {lang_code}")


def get_language() -> str:
    return _current_language


def tr(key: str, **kwargs) -> str:
    """Вернуть переведённую строку по ключу, с подстановкой параметров."""
    entry = STRINGS.get(key)
    if entry is None:
        return key  # чтобы отсутствие перевода было видно, а не падало
    text = entry.get(_current_language, entry.get("ru", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
