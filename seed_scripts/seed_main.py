"""Главный seed-скрипт: полная переинициализация контента марафона.

Запуск: python3 seed_scripts/seed_main.py

Порядок шагов важен из-за внешних ключей:
    очистка таблиц -> articles -> idioms -> weeks -> lessons -> exercises ->
    words -> word_lesson_assignments -> grammar_tags -> grammar_rules ->
    reading -> novel (реплики новеллы, отдельным async-подключением через SQLAlchemy)

Не идемпотентен по дизайну: перед запуском таблицы контента полностью
очищаются (TRUNCATE ... CASCADE). Таблица users и все user_*_progress
(кроме тех, что каскадно зависят от очищаемых таблиц) не трогаются.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_scripts.db import get_connection
from seed_scripts.seed_articles import seed_articles
from seed_scripts.seed_idioms import seed_idioms
from seed_scripts.seed_weeks import seed_weeks
from seed_scripts.seed_lessons import seed_lessons
from seed_scripts.seed_exercises import seed_exercises
from seed_scripts.seed_words import seed_words, seed_word_lesson_assignments
from seed_scripts.seed_grammar import seed_grammar_tags, seed_grammar_rules
from seed_scripts.seed_reading import seed_reading
from seed_scripts.seed_novel import main as seed_novel

# ──────────────────────────────────────────────────────────────
# Очистка таблиц контента (в правильном порядке с учётом FK)
# ──────────────────────────────────────────────────────────────
TRUNCATE_STATEMENTS = [
    "TRUNCATE reading_questions CASCADE;",
    "TRUNCATE reading_texts CASCADE;",
    "TRUNCATE user_idiom_progress CASCADE;",
    "TRUNCATE idioms CASCADE;",
    "TRUNCATE exercises CASCADE;",
    "TRUNCATE lesson_word_association CASCADE;",
    "TRUNCATE user_lesson_progress CASCADE;",
    "TRUNCATE user_week_progress CASCADE;",
    "TRUNCATE lessons CASCADE;",
    "TRUNCATE weeks CASCADE;",
    "TRUNCATE words CASCADE;",
    "TRUNCATE grammar_rule_tags CASCADE;",
    "TRUNCATE grammar_rules CASCADE;",
    "TRUNCATE grammar_tags CASCADE;",
    "TRUNCATE articles CASCADE;",
]


def wipe_tables(cur):
    print("🧹 Очищаю таблицы контента (TRUNCATE ... CASCADE)...")
    for stmt in TRUNCATE_STATEMENTS:
        cur.execute(stmt)
        print(f"   {stmt}")


def run():
    conn = get_connection()
    cur = conn.cursor()
    try:
        wipe_tables(cur)
        conn.commit()

        seed_articles(cur)
        conn.commit()

        seed_idioms(cur)
        conn.commit()

        week_ids = seed_weeks(cur)
        conn.commit()

        lesson_ids = seed_lessons(cur, week_ids)
        conn.commit()

        seed_exercises(cur, lesson_ids)
        conn.commit()

        word_ids = seed_words(cur)
        conn.commit()

        seed_word_lesson_assignments(cur, word_ids, lesson_ids)
        conn.commit()

        tag_id_map = seed_grammar_tags(cur)
        conn.commit()

        seed_grammar_rules(cur, tag_id_map)
        conn.commit()

        seed_reading(cur, week_ids)
        conn.commit()

        print("\n✅ Готово! База переинициализирована новым контентом.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    asyncio.run(seed_novel())


if __name__ == "__main__":
    run()
