"""
Правила начисления монет/опыта и выдачи значков.
Вынесено отдельно, чтобы баланс игры можно было настраивать,
не трогая экраны и базу данных.
"""

COINS_PER_CORRECT_FIRST_TRY = 10
COINS_PER_CORRECT_RETRY = 5
XP_PER_CORRECT = 15
XP_PER_TOPIC_COMPLETE = 50

BADGES = {
    "first_task": {"ru": "Первые шаги", "kk": "Алғашқы қадам", "en": "First steps"},
    "topic_master": {"ru": "Мастер темы", "kk": "Тақырып шебері", "en": "Topic master"},
    "streak_3": {"ru": "3 дня подряд", "kk": "Қатарынан 3 күн", "en": "3-day streak"},
    "math_explorer": {"ru": "Исследователь чисел", "kk": "Сандар зерттеушісі", "en": "Number explorer"},
    "bookworm": {"ru": "Книжный червячок", "kk": "Кітап құрты", "en": "Bookworm"},
}


def reward_for_answer(is_correct: bool, attempts: int) -> dict:
    if not is_correct:
        return {"coins": 0, "xp": 0}
    coins = COINS_PER_CORRECT_FIRST_TRY if attempts == 1 else COINS_PER_CORRECT_RETRY
    return {"coins": coins, "xp": XP_PER_CORRECT}


def reward_for_topic_completion(correct_count: int, total_count: int) -> dict:
    """Возвращает бонус + количество звёзд (0-3) за прохождение темы."""
    accuracy = correct_count / total_count if total_count else 0
    if accuracy == 1:
        stars = 3
    elif accuracy >= 0.7:
        stars = 2
    elif accuracy > 0:
        stars = 1
    else:
        stars = 0
    return {"coins": 20, "xp": XP_PER_TOPIC_COMPLETE, "stars": stars}
