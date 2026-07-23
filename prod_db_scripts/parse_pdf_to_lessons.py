"""Парсер chinese_full_course_final.pdf в структурированные данные уроков.

Извлекает через pdfplumber (проверено на реальном файле):
  - границы дней: каждый день в этом PDF гарантированно начинается с новой
    страницы заголовком "День N. ..." — поэтому разбиение по дням идёт по
    номерам страниц, а не по эвристикам на сплошном тексте;
  - таблицы «Новые слова» — через page.extract_tables() (у audio-тегов
    Word-экспорт закрывающий </audio> иногда переносит на отдельную строку
    таблицы; парсер это учитывает — см. _extract_vocab_rows);
  - диалоги — построчным regex по шаблону
    "Имя [pinyin] Речь: — 汉字 (Pīnyīn) — перевод" и
    "{{user_name}}: — 汉字 (Pīnyīn) — перевод".

ВАЖНЫЙ ИЗВЕСТНЫЙ НЕДОСТАТОК (проверено вручную на странице 34 / День 7):
    Родительский pinyin у части диалоговых строк (диалоги-повторения в днях
    7/14/21/27) в текстовом слое PDF просто ОТСУТСТВУЕТ — это не баг парсера,
    а особенность экспорта самого PDF (в .docx-версии этого же курса этот
    текст, судя по всему, есть, раз он попал в исходную расшифровку).
    Парсер в этом случае восстанавливает pinyin автоматически через
    pypinyin (с тоновыми знаками) — это лучшее приближение, но при
    ответственном использовании стоит свериться с оригиналом.

Это НЕ замена prod_db_scripts/seed_lessons_v2.py (который выверен вручную
по расшифровке курса и содержит готовую тему/диалоги в HTML). Это —
инструмент для будущей автогенерации/сверки, если курс/PDF будут обновляться.

Использование:
    python3 prod_db_scripts/parse_pdf_to_lessons.py chinese_full_course_final.pdf
    python3 prod_db_scripts/parse_pdf_to_lessons.py course.pdf --dump-json out.json
    python3 prod_db_scripts/parse_pdf_to_lessons.py course.pdf --diff-dialogues
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field

import pdfplumber
from pypinyin import Style, pinyin as pypinyin_pinyin

DAY_HEADER_RE = re.compile(r"^День (\d+)\.\s*(.*)$")
VOCAB_HEADER_RE = re.compile(r"^Новые слова")
# "2. Прочитайте диалоги" (дни повторения) и "1. Большой диалог: ..." (день 27)
# — оба варианта заголовка секции с диалогом(-ами).
DIALOGUE_HEADER_RE = re.compile(r"^Диалог\b|^\d+\.\s*.*[Дд]иалог")
EXERCISES_HEADER_RE = re.compile(r"^УПРАЖНЕНИЯ")
# Начало новой пронумерованной секции теории (например, "2. Расскажите о
# себе" после диалога в дне 27) — сигнал закончить сбор реплик диалога, даже
# если ЗАДАНИЯ/УПРАЖНЕНИЯ ещё не начались.
NEW_SECTION_RE = re.compile(r"^\d+\.\s")
AUDIO_TAG_RE = re.compile(r'audio src="([^"]*)')

DIALOGUE_LINE_RE = re.compile(
    r"^(?:(?P<hanzi_name>[一-鿿]+)\s*\[(?P<py_name>[^\]]+)\]\s*(?P<display>[^:]+)"
    r"|(?P<user>\{\{user_name\}\}))\s*:\s*—\s*(?P<rest>.+)$"
)
HANZI_PINYIN_SPLIT_RE = re.compile(r"^(?P<hanzi>.+?)\s*\((?P<pinyin>[^()]+)\)\s*$")

# Известные персонажи курса -> слаг для data-character (совпадает с
# CHARACTER_SLUGS в seed_lessons_v2.py). Для новых имён используется
# грубая транслитерация кириллицы как запасной вариант.
KNOWN_CHARACTER_SLUGS = {
    "Жулан": "zhulan",
    "Конфуси": "konfusi",
    "Чингису": "chingisu",
    "Брис Лэй": "bris_lei",
    "Жо": "zho",
}

_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya", " ": "_",
}


def slugify_character(display_name: str) -> str:
    if display_name in KNOWN_CHARACTER_SLUGS:
        return KNOWN_CHARACTER_SLUGS[display_name]
    return "".join(_CYR_TO_LAT.get(ch, ch) for ch in display_name.lower())


def hanzi_to_pinyin(hanzi: str) -> str:
    """Запасной вариант, когда в тексте PDF пиньинь отсутствует."""
    syllables = pypinyin_pinyin(hanzi, style=Style.TONE)
    return " ".join(s[0] for s in syllables)


@dataclass
class DialogueLine:
    speaker: str  # "{{user_name}}" или отображаемое имя персонажа
    character: str  # слаг для data-character
    hanzi: str
    pinyin: str
    pinyin_is_reconstructed: bool
    ru: str


@dataclass
class VocabEntry:
    hanzi: str
    pinyin: str
    ru: str


@dataclass
class LessonRaw:
    day: int
    title: str
    theory_lines: list = field(default_factory=list)
    vocab: list = field(default_factory=list)  # list[VocabEntry]
    dialogues: list = field(default_factory=list)  # list[list[DialogueLine]]


def _extract_vocab_rows(tables: list) -> list:
    """См. docstring модуля: строки-«хвосты» (перенос закрывающего тега на
    следующую строку таблицы) распознаются по тому, что в них нет пиньиня
    и перевода, и просто пропускаются."""
    entries = []
    for table in tables:
        header = table[0] if table else []
        header_text = " ".join(c or "" for c in header)
        if "Иероглиф" not in header_text or "Пиньинь" not in header_text:
            continue
        for row in table[1:]:
            cells = [c.strip() for c in row if c and c.strip()]
            if len(cells) < 3:
                continue
            hanzi_cell, pinyin_cell, translation_cell = cells[0], cells[1], cells[-1]
            m = AUDIO_TAG_RE.search(hanzi_cell)
            if not m:
                continue
            hanzi = m.group(1).strip()
            if not hanzi:
                continue
            entries.append(VocabEntry(hanzi=hanzi, pinyin=pinyin_cell, ru=translation_cell))
    return entries


def _parse_dialogue_block(lines: list) -> list:
    """lines: список строк текста внутри диалогового блока (уже без
    заголовка «Диалог» и без строки с общим <audio> всего диалога)."""
    turns = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("<audio"):
            continue
        m = DIALOGUE_LINE_RE.match(line)
        if not m:
            # Перевод длинной реплики иногда переносится PDF-типографикой на
            # отдельную строку без префикса "Имя: —" — считаем её продолжением
            # русского перевода предыдущей реплики.
            if turns:
                turns[-1].ru = f"{turns[-1].ru} {line}".strip()
            continue
        rest = m.group("rest")
        # Разделитель "汉字(pīnyīn) — перевод" не всегда содержит пробел перед
        # тире: после китайской пунктуации (？！。) типографика PDF пробел не
        # ставит, поэтому режем по тире с необязательными пробелами вокруг.
        parts = re.split(r"\s*—\s*", rest, maxsplit=1)
        if len(parts) != 2:
            continue
        hanzi_pinyin_part, ru = parts[0].strip(), parts[1].strip()
        hp_match = HANZI_PINYIN_SPLIT_RE.match(hanzi_pinyin_part)
        reconstructed = False
        if hp_match:
            hanzi = hp_match.group("hanzi").strip()
            pinyin = hp_match.group("pinyin").strip()
        else:
            hanzi = hanzi_pinyin_part
            pinyin = hanzi_to_pinyin(hanzi)
            reconstructed = True

        if m.group("user"):
            speaker, character = "{{user_name}}", "user"
        else:
            speaker = m.group("display").strip()
            character = slugify_character(speaker)

        turns.append(
            DialogueLine(
                speaker=speaker,
                character=character,
                hanzi=hanzi,
                pinyin=pinyin,
                pinyin_is_reconstructed=reconstructed,
                ru=ru,
            )
        )
    return turns


def parse_pdf(path: str) -> list:
    """Возвращает список LessonRaw, по одному на каждый из 28 дней."""
    with pdfplumber.open(path) as pdf:
        day_starts = []  # (page_index, day_number, title)
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            first_line = text.split("\n", 1)[0] if text else ""
            m = DAY_HEADER_RE.match(first_line)
            if m:
                day_starts.append((i, int(m.group(1)), m.group(2).strip()))

        lessons = []
        for idx, (start_page, day, title) in enumerate(day_starts):
            end_page = day_starts[idx + 1][0] if idx + 1 < len(day_starts) else len(pdf.pages)

            theory_lines: list = []
            vocab: list = []
            dialogues: list = []
            current_dialogue_lines: list = []
            in_dialogue = False
            in_exercises = False

            for p in range(start_page, end_page):
                page = pdf.pages[p]
                text = page.extract_text() or ""
                page_lines = text.split("\n")

                if not in_exercises:
                    vocab.extend(_extract_vocab_rows(page.extract_tables()))

                for line in page_lines:
                    stripped = line.strip()
                    if EXERCISES_HEADER_RE.match(stripped):
                        if current_dialogue_lines:
                            turns = _parse_dialogue_block(current_dialogue_lines)
                            if turns:
                                dialogues.append(turns)
                            current_dialogue_lines = []
                        in_exercises = True
                        in_dialogue = False
                        continue
                    if in_exercises:
                        continue
                    if DIALOGUE_HEADER_RE.match(stripped):
                        if current_dialogue_lines:
                            turns = _parse_dialogue_block(current_dialogue_lines)
                            if turns:
                                dialogues.append(turns)
                            current_dialogue_lines = []
                        in_dialogue = True
                        continue
                    if in_dialogue and NEW_SECTION_RE.match(stripped):
                        # Новая пронумерованная секция теории (например,
                        # "2. Расскажите о себе" в дне 27) — диалог закончился.
                        if current_dialogue_lines:
                            turns = _parse_dialogue_block(current_dialogue_lines)
                            if turns:
                                dialogues.append(turns)
                            current_dialogue_lines = []
                        in_dialogue = False
                    if in_dialogue:
                        current_dialogue_lines.append(line)
                    elif not VOCAB_HEADER_RE.match(stripped):
                        # Таблицы слов уже извлечены отдельно через extract_tables();
                        # остальной текст (теория) складываем как есть, "на глаз" —
                        # это приближённая реконструкция, см. docstring модуля.
                        theory_lines.append(line)

            if current_dialogue_lines:
                turns = _parse_dialogue_block(current_dialogue_lines)
                if turns:
                    dialogues.append(turns)

            lessons.append(
                LessonRaw(
                    day=day,
                    title=f"День {day}. {title}",
                    theory_lines=theory_lines,
                    vocab=vocab,
                    dialogues=dialogues,
                )
            )
        return lessons


def lessons_to_dict(lessons: list) -> list:
    return [
        {
            "day": lesson.day,
            "title": lesson.title,
            "vocab": [asdict(v) for v in lesson.vocab],
            "dialogues": [[asdict(line) for line in turns] for turns in lesson.dialogues],
            "theory_lines": lesson.theory_lines,
        }
        for lesson in lessons
    ]


def diff_against_seed_v2(lessons: list) -> int:
    """Сверяет извлечённые из PDF диалоги с data-audio/переводами, уже
    вручную занесёнными в seed_lessons_v2.LESSONS_DATA_V2. Возвращает
    количество найденных расхождений (0 — всё совпало)."""
    import os as _os

    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from prod_db_scripts.seed_lessons_v2 import LESSONS_DATA_V2

    seed_by_day = {day: html for day, _, html in LESSONS_DATA_V2}
    mismatches = 0
    for lesson in lessons:
        html = seed_by_day.get(lesson.day, "")
        pdf_hanzi = [
            line.hanzi
            for turns in lesson.dialogues
            for line in turns
        ]
        for hanzi in pdf_hanzi:
            if hanzi and hanzi not in html:
                mismatches += 1
                print(f"⚠️  День {lesson.day}: реплика из PDF не найдена в seed_lessons_v2: {hanzi!r}")
    if mismatches == 0:
        print("✅ Все реплики диалогов из PDF найдены в seed_lessons_v2.LESSONS_DATA_V2.")
    return mismatches


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf_path", help="Путь к PDF-файлу курса")
    parser.add_argument("--dump-json", metavar="PATH", help="Сохранить извлечённые данные в JSON")
    parser.add_argument(
        "--diff-dialogues",
        action="store_true",
        help="Сверить извлечённые диалоги с prod_db_scripts/seed_lessons_v2.py",
    )
    args = parser.parse_args()

    lessons = parse_pdf(args.pdf_path)
    print(f"Распознано дней: {len(lessons)}")
    for lesson in lessons:
        n_dialogue_lines = sum(len(t) for t in lesson.dialogues)
        print(
            f"  День {lesson.day:>2}: слов={len(lesson.vocab):>2}, "
            f"диалогов={len(lesson.dialogues)}, реплик={n_dialogue_lines}"
        )

    if args.dump_json:
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(lessons_to_dict(lessons), f, ensure_ascii=False, indent=2)
        print(f"📄 Сохранено: {args.dump_json}")

    if args.diff_dialogues:
        print()
        diff_against_seed_v2(lessons)


if __name__ == "__main__":
    main()
