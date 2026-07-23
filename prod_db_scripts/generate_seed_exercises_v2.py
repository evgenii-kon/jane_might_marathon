"""Генерирует prod_db_scripts/seed_exercises_v2.py из результатов
parse_exercises.py (полный автоматический разбор PDF-курса).

Используется один раз для материализации EXERCISES_DATA_V2 в виде обычного
Python-литерала (без обязательной зависимости от pdfplumber/PDF-файла при
последующих запусках seed'а). Если курс/PDF изменится — просто перезапустите
этот генератор заново.

Использование:
    python3 prod_db_scripts/generate_seed_exercises_v2.py chinese_full_course_final.pdf
"""

import sys

from parse_exercises import parse_exercises


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 prod_db_scripts/generate_seed_exercises_v2.py <path.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    results = parse_exercises(pdf_path)

    rows = []
    total_skipped = 0
    for d in results:
        for order_n, r in enumerate(d.rows, start=1):
            rows.append((d.day, order_n, r.type, r.question_text, r.config, r.explanation))
        total_skipped += len(d.skipped)

    out_path = "prod_db_scripts/seed_exercises_v2.py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        f.write("EXERCISES_DATA_V2 = [\n")
        for day, order_n, ex_type, question, config, explanation in rows:
            f.write(
                f"    ({day!r}, {order_n!r}, {ex_type!r}, {question!r}, {config!r}, {explanation!r}),\n"
            )
        f.write("]\n")
        f.write(FOOTER)

    print(f"📄 Записано {len(rows)} упражнений в {out_path}")
    print(f"⚠️  Пропущено при разборе (не попали в файл): {total_skipped} блок(ов) — см. вывод parse_exercises.py --show-skipped")


HEADER = '''"""Seed v2: упражнения (exercises) курса «Китайский с нуля», 28 дней.

В отличие от seed_scripts/seed_exercises.py (только тип quiz, данные из
seed_scripts/seed_lessons.py), этот файл:
  - содержит ВСЕ упражнения курса из chinese_full_course_final.pdf, всех
    типов (quiz, audio_quiz, matching_pairs, build_word, translate,
    fill_blank_open);
  - сгенерирован автоматически прогоном
    prod_db_scripts/generate_seed_exercises_v2.py по PDF (сам парсер —
    prod_db_scripts/parse_exercises.py) и НЕ редактируется вручную построчно
    — при необходимости точечных правок правьте, но при повторной генерации
    правки будут перезаписаны;
  - дни 7, 14, 21, 28 (дни повторения) не содержат упражнений в этом файле —
    в PDF там либо большой контрольный тест другого формата, либо раздел не
    предназначен для интерактивных упражнений.

audio_url в config для типов audio_quiz — иероглифы-плейсхолдеры (как
data-audio в prod_db_scripts/seed_lessons_v2.py); после сида их нужно
прогнать через audio_generator.py, который заменит их на реальные ссылки в
S3 (ищет по паттерну \\"audio_url\\": \\"<иероглифы>\\").

Запуск: python3 prod_db_scripts/seed_exercises_v2.py
"""

import os
import sys

import psycopg2.extras

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


'''

FOOTER = '''

def seed_exercises_v2(cur, lesson_ids, exercises_data=None):
    """Полностью заменяет содержимое таблицы exercises данными из
    exercises_data (по умолчанию — EXERCISES_DATA_V2 из этого модуля).
    lesson_ids — словарь {lesson.name: lesson.id}
    (имена вида "День N. ...", как в prod_db_scripts/seed_lessons_v2.py)."""
    if exercises_data is None:
        exercises_data = EXERCISES_DATA_V2
    print("\\n🗑️  Удаляю старые упражнения...")
    cur.execute("SELECT COUNT(*) FROM user_exercise_progress")
    progress_count = cur.fetchone()[0]
    if progress_count:
        print(f"   ⚠️ Удаляю также {progress_count} запись(ей) user_exercise_progress "
              f"(ссылаются на заменяемые упражнения)")
        cur.execute("DELETE FROM user_exercise_progress")
    cur.execute("DELETE FROM exercises")

    print("📝 Вставляю упражнения v2...")
    inserted = 0
    skipped_days = set()
    for day, order_n, ex_type, question, config, explanation in exercises_data:
        lesson_name = next((n for n in lesson_ids if n.startswith(f"День {day}.")), None)
        if not lesson_name:
            skipped_days.add(day)
            continue
        lesson_id = lesson_ids[lesson_name]
        cur.execute(
            """INSERT INTO exercises
               (lesson_id, type, question_text, config, explanation, order_in_lesson)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (lesson_id, ex_type, question, psycopg2.extras.Json(config), explanation, order_n),
        )
        inserted += 1
    for day in sorted(skipped_days):
        print(f"   ⚠️ Урок для дня {day} не найден в lesson_ids, пропускаю его упражнения")
    print(f"   ✅ Вставлено упражнений: {inserted}")


def invalidate_exercises_cache():
    """ExerciseService кэширует в Redis под префиксом 'exercise' (см.
    app/services/exercise_service.py) — без инвалидации сайт мог бы отдавать
    старые упражнения/список до истечения TTL (обычно 300 секунд)."""
    import os as _os

    try:
        import redis as redis_sync
    except ImportError:
        print("⚠️  Пакет redis не установлен — пропускаю инвалидацию кэша упражнений.")
        return

    host = _os.getenv("REDIS_HOST", "localhost")
    port = int(_os.getenv("REDIS_PORT", 6379))
    db = int(_os.getenv("REDIS_DB", 0))
    password = _os.getenv("REDIS_PASSWORD") or None

    try:
        client = redis_sync.Redis(host=host, port=port, db=db, password=password)
        keys = client.keys("exercise:*")
        if keys:
            client.delete(*keys)
        print(f"🧹 Инвалидировал кэш упражнений в Redis ({len(keys)} ключ(ей) exercise:*).")
    except Exception as exc:
        print(f"⚠️  Не удалось инвалидировать кэш упражнений в Redis ({exc}).")


def run(module_path: str = None):
    """module_path — необязательный путь к альтернативному .py-файлу,
    определяющему EXERCISES_DATA_V2 (например, файл с уже подставленными
    аудио-ссылками, полученный через audio_generator.py). Если не указан —
    используются данные из этого модуля (без ссылок на аудио в audio_url)."""
    from seed_scripts.db import get_connection

    exercises_data = EXERCISES_DATA_V2
    if module_path:
        import importlib.util

        spec = importlib.util.spec_from_file_location("_seed_exercises_v2_external", module_path)
        external = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external)
        exercises_data = external.EXERCISES_DATA_V2
        print(f"📄 Использую EXERCISES_DATA_V2 из {module_path} ({len(exercises_data)} упражнений)")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, id FROM lessons")
        lesson_ids = dict(cur.fetchall())
        if not lesson_ids:
            raise RuntimeError(
                "Таблица lessons пуста. Сначала выполните "
                "prod_db_scripts/seed_lessons_v2.py (или seed_scripts/seed_main.py)."
            )
        seed_exercises_v2(cur, lesson_ids, exercises_data=exercises_data)
        conn.commit()
        print("\\n✅ Готово! Упражнения (v2) обновлены.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    invalidate_exercises_cache()


if __name__ == "__main__":
    import sys as _sys

    run(_sys.argv[1] if len(_sys.argv) > 1 else None)
'''


if __name__ == "__main__":
    main()
