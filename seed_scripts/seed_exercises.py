"""Seed: упражнения (exercises) для уроков, данные берутся из seed_lessons.LESSONS_DATA."""

import psycopg2.extras

from seed_scripts.seed_lessons import LESSONS_DATA

def seed_exercises(cur, lesson_ids):
    """Создаёт упражнения для уроков из LESSONS_DATA (дни 7/14/21/28 — без упражнений)."""
    print("\n📝 Вставляю упражнения...")
    total = 0
    for _day, name, _content_html, exercises in LESSONS_DATA:
        if not exercises:
            continue
        lesson_id = lesson_ids[name]
        for desc, question, o1, o2, o3, o4, correct, explanation, order_n in exercises:
            config = {
                "topic": desc,
                "options": [o1, o2, o3, o4],
                "correct": correct - 1,  # в LESSONS_DATA correct 1-based, в config — 0-based
            }
            cur.execute(
                """INSERT INTO exercises
                   (lesson_id, type, question_text, config, explanation, order_in_lesson)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (lesson_id, "quiz", question, psycopg2.extras.Json(config), explanation, order_n),
            )
            total += 1
    print(f"   ✅ Вставлено упражнений: {total}")

