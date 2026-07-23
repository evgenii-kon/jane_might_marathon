"""Парсер упражнений (раздел «УПРАЖНЕНИЯ» каждого дня) из
chinese_full_course_final.pdf в список строк для EXERCISES_DATA_V2
(см. prod_db_scripts/seed_exercises_v2.py).

Дни 7, 14, 21, 28 — дни повторения без раздела «УПРАЖНЕНИЯ» в нужном нам
формате (там либо большой финальный тест другого формата, либо раздел не
нужен по ТЗ) — пропускаются целиком.

В PDF десять паттернов заданий (обозначены в тексте как «[Паттерн X — ...]»).
Часть из них при ближайшем рассмотрении структурно идентична (например,
единственный «Паттерн Г — Собери правило» на весь курс на самом деле —
обычный вопрос с выбором из вариантов, как «Паттерн А»), поэтому диспетчеризация
здесь идёт в первую очередь по СТРУКТУРЕ текста блока, а не только по
заявленной метке паттерна.

Использование:
    python3 prod_db_scripts/parse_exercises.py chinese_full_course_final.pdf
    python3 prod_db_scripts/parse_exercises.py course.pdf --dump-json out.json
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field

import pdfplumber

EXCLUDED_DAYS = {7, 14, 21, 28}

DAY_HEADER_RE = re.compile(r"^День (\d+)\.\s*(.*)$")
EXERCISES_HEADER_RE = re.compile(r"^УПРАЖНЕНИЯ\s*$")
HOMEWORK_HEADER_RE = re.compile(r"^Домашнее задание\s*$")
TASK_HEADER_RE = re.compile(
    r"^Задание\s+(\d+)\.\s*\[Паттерн\s+([^\]—]+)—\s*([^\]]+)\]\s*(.*)$"
)
AUDIO_TAG_RE = re.compile(r'<audio src="([^"]*)"></audio>')
CHECK_LINE_RE = re.compile(r"^✓\s*(.*)$")
NUMBERED_ITEM_START_RE = re.compile(r"^(\d+)\.\s*(.*)$")
# Лукбихайнд не даёт спутать реальный маркер варианта ("... б) значение")
# со случайным совпадением внутри обычного слова, оканчивающегося на одну
# из этих букв прямо перед скобкой (например, "она)" внутри "тā — она)" —
# без лукбихайнда буква "а" перед ")" ошибочно читалась бы как маркер "а)").
OPTION_MARKER_RE = re.compile(r"(?<![а-яёА-ЯЁa-zA-Z])([абвг])\)\s*")


def _find_option_markers(text: str) -> list:
    """Как OPTION_MARKER_RE, но дополнительно учитывает глубину вложенности
    круглых скобок: маркер засчитывается только ВНЕ скобок. Это нужно,
    потому что помимо случая "она)" (см. OPTION_MARKER_RE) в тексте
    встречается и обратная ловушка — русская подсказка вида "(иду в)",
    где закрывающая скобка стоит сразу после однобуквенного предлога "в",
    что снаружи неотличимо от настоящего маркера "в) значение" одной лишь
    проверкой "не после буквы" (предлогу предшествует пробел, как и
    маркеру). Возвращает список (start, end) — start на самой букве,
    end — после ")" и последующих пробелов."""
    markers = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            depth += 1
            i += 1
            continue
        if ch == ")":
            if depth > 0:
                depth -= 1
            i += 1
            continue
        if depth == 0 and ch in "абвг" and i + 1 < n and text[i + 1] == ")":
            prev = text[i - 1] if i > 0 else None
            if prev is None or not prev.isalpha():
                j = i + 2
                while j < n and text[j] == " ":
                    j += 1
                markers.append((i, j))
                i = j
                continue
        i += 1
    return markers
LETTER_TO_INDEX = {"а": 0, "б": 1, "в": 2, "г": 3}

# Русские переводы для 26 уникальных ответов «Паттерн Г — Собери предложение»
# (в самом PDF рядом с этими заданиями перевод не даётся — только скремблированные
# китайские слова и китайский же ✓-ответ, поэтому перевод сопоставлен вручную по
# смыслу урока).
SENTENCE_TRANSLATIONS = {
    "一只猫": "одна кошка",
    "两本书": "две книги",
    "书在桌子上面。": "Книга на столе.",
    "今天星期几？": "Какой сегодня день недели?",
    "他十二岁。": "Ему двенадцать лет.",
    "他晚上看电视。": "Вечером он смотрит телевизор.",
    "他看书。": "Он читает книгу.",
    "你叫什么名字？": "Как тебя зовут?",
    "你在哪儿？": "Ты где?",
    "你多大？": "Сколько тебе лет?",
    "你是哪国人？": "Ты из какой страны?",
    "我七点起床。": "Я встаю в семь часов.",
    "我买了一本书。": "Я купил книгу.",
    "我们十二点吃饭。": "Мы обедаем в двенадцать часов.",
    "我们学习汉语。": "Мы учим китайский.",
    "我们都是学生。": "Мы все студенты.",
    "我住在北京。": "Я живу в Пекине.",
    "我喝水。": "Я пью воду.",
    "我坐出租车回家。": "Я еду домой на такси.",
    "我坐飞机去北京。": "Я лечу в Пекин на самолёте.",
    "我家有四口人。": "В моей семье четыре человека.",
    "我想喝茶。": "Я хочу выпить чаю.",
    "我早上七点起床。": "Я встаю в семь утра.",
    "我是俄罗斯人，是学生。": "Я россиянин, я студент.",
    "这个多少钱？": "Сколько это стоит?",
    "这是谁的书？": "Чья это книга?",
}


@dataclass
class ExerciseRow:
    type: str
    question_text: str
    config: dict
    explanation: str = ""


@dataclass
class DayExercises:
    day: int
    rows: list = field(default_factory=list)  # list[ExerciseRow]
    skipped: list = field(default_factory=list)  # list[str] (raw block text, для ручного разбора)


# ──────────────────────────────────────────────────────────────
# Границы дней (переиспользуем идею из parse_pdf_to_lessons.py)
# ──────────────────────────────────────────────────────────────


def find_day_page_ranges(pdf) -> list:
    day_starts = []
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").strip()
        first_line = text.split("\n", 1)[0] if text else ""
        m = DAY_HEADER_RE.match(first_line)
        if m:
            day_starts.append((i, int(m.group(1))))
    ranges = []
    for idx, (start_page, day) in enumerate(day_starts):
        end_page = day_starts[idx + 1][0] if idx + 1 < len(day_starts) else len(pdf.pages)
        ranges.append((day, start_page, end_page))
    return ranges


def extract_exercises_section(pdf, start_page: int, end_page: int) -> str:
    """Текст между заголовком «УПРАЖНЕНИЯ» и первым «Домашнее задание»
    (включительно по границам, но без этих двух заголовочных строк)."""
    lines = []
    for p in range(start_page, end_page):
        text = pdf.pages[p].extract_text() or ""
        lines.extend(text.split("\n"))

    started = False
    collected = []
    for line in lines:
        stripped = line.strip()
        if not started:
            if EXERCISES_HEADER_RE.match(stripped):
                started = True
            continue
        if HOMEWORK_HEADER_RE.match(stripped):
            break
        collected.append(line)
    return "\n".join(collected)


# ──────────────────────────────────────────────────────────────
# Разбиение на блоки «Задание N. [Паттерн X — Y] Заголовок»
# ──────────────────────────────────────────────────────────────


def split_into_task_blocks(section_text: str) -> list:
    """Возвращает список (task_num, pattern_letter, pattern_kind, title, body_lines)."""
    lines = section_text.split("\n")
    blocks = []
    current = None
    for line in lines:
        m = TASK_HEADER_RE.match(line.strip())
        if m:
            if current:
                blocks.append(current)
            task_num = int(m.group(1))
            pattern_letter = m.group(2).strip()
            pattern_kind = m.group(3).strip()
            title = m.group(4).strip()
            current = {
                "task_num": task_num,
                "pattern_letter": pattern_letter,
                "pattern_kind": pattern_kind,
                "title": title,
                "lines": [],
            }
        elif current is not None:
            current["lines"].append(line)
    if current:
        blocks.append(current)
    return blocks


# ──────────────────────────────────────────────────────────────
# Общие хелперы
# ──────────────────────────────────────────────────────────────


def _find_check_line_index(lines: list) -> int:
    for i, line in enumerate(lines):
        if CHECK_LINE_RE.match(line.strip()):
            return i
    return -1


EXPLANATIONS_HEADER_RE = re.compile(r"^Пояснения\s*:")


def _get_check_text(lines: list, check_idx: int) -> str:
    """Строка ✓-ответа иногда переносится PDF-типографикой на следующую(-ие)
    физическую(-ие) строку(-и) (например, длинный список "1) ... 8) ...")
    — здесь они склеиваются в одну строку. Останавливается перед
    "Пояснения: ..." (отдельным блоком с текстовыми уточнениями, не
    относящимся к самим значениям ответов)."""
    parts = [CHECK_LINE_RE.match(lines[check_idx].strip()).group(1)]
    for line in lines[check_idx + 1:]:
        s = line.strip()
        if not s:
            continue
        if EXPLANATIONS_HEADER_RE.match(s):
            break
        parts.append(s)
    return " ".join(parts)


def _split_answers(raw: str, expected_count: int) -> list:
    """Разбивает строку-список ответов на РОВНО expected_count значений.
    Значения сами могут содержать цифры (номер тона "1"/"2"/...) и даже
    "N)"-подобные фрагменты внутри скобочных примечаний (например,
    "Сколько тебе лет? (до 10)" перед "2) Мне 9 лет...") — поэтому вместо
    "найди любой \\d+\\)" ищем СТРОГО последовательные маркеры 1),2),...,N)
    (используя лукбихайнд, чтобы не попасть на конец многозначного числа
    вроде "10)"). Возвращает [] если разбить не удалось.

    Поддерживает также запасной вариант "значение · значение · ..." (без
    номеров, через точку-разделитель) — используется в Паттернах В/К/Г.
    """
    raw = raw.strip()
    if not raw or expected_count <= 0:
        return []

    if expected_count == 1:
        if "·" in raw:
            parts = [v.strip() for v in raw.split("·") if v.strip()]
            if len(parts) == 1:
                return parts
        return [raw]

    positions = []
    pos = 0
    ok = True
    for n in range(1, expected_count + 1):
        m = re.search(rf"(?<!\d){n}\)\s*", raw[pos:])
        if not m:
            ok = False
            break
        positions.append((pos + m.start(), pos + m.end()))
        pos = pos + m.end()
    if ok:
        values = []
        for i in range(expected_count):
            start = positions[i][1]
            end = positions[i + 1][0] if i + 1 < expected_count else len(raw)
            values.append(raw[start:end].strip())
        if all(values):
            return values

    if "·" in raw:
        parts = [v.strip() for v in raw.split("·") if v.strip()]
        if len(parts) == expected_count:
            return parts

    return []


def _strip_paren_note(value: str) -> str:
    """«天 (日)» -> «天» (отбрасываем скобочную альтернативу/примечание)."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", value).strip()


# ──────────────────────────────────────────────────────────────
# Паттерн Б — Соедини пары -> matching_pairs
# ──────────────────────────────────────────────────────────────

ARROW_LINE_RE = re.compile(r"^(?P<left>.+?)\s*←→\s*(?P<right>.+)$")


# Ручные подстановки для редких блоков «Паттерн Б», где ✓-строка не
# восстанавливает пары в тексте (напр. "✓ По диалогу урока"), а отсылает к
# уже пройденному в уроке диалогу — там пара берётся из смысла диалога.
PATTERN_B_OVERRIDES = {
    (2, 6): [
        {"left": "你是老师吗？", "right": "我不是老师，我是学生。"},
        {"left": "他也是学生吗？", "right": "是，他也是学生。"},
    ],
}


def parse_pattern_b(block: dict, day: int = None) -> list:
    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return []
    check_text = _get_check_text(block["lines"], check_idx)
    # Строка ✓ может продолжаться (редко) — но у Паттерна Б всегда умещается в одну строку.

    lefts = []
    for line in block["lines"][:check_idx]:
        m = ARROW_LINE_RE.match(line.strip())
        if m:
            lefts.append(m.group("left").strip())
    if not lefts:
        return None  # не распознано

    override = PATTERN_B_OVERRIDES.get((day, block["task_num"]))
    if override:
        pairs = override
    else:
        # Ищем в ✓-строке позиции каждого left-токена, за которым следует "—".
        positions = []
        for token in lefts:
            m = re.search(re.escape(token) + r"\s*—", check_text)
            if m:
                positions.append((m.start(), token, m.end()))
        if len(positions) != len(lefts):
            return None  # не все токены нашлись — сигнал ручной проверки
        positions.sort(key=lambda t: t[0])

        pairs = []
        for i, (start, token, value_start) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(check_text)
            right = check_text[value_start:end].strip()
            pairs.append({"left": token, "right": right})

    question_text = block["title"] or "Соедините пары"
    row = ExerciseRow(
        type="matching_pairs",
        question_text=question_text,
        config={"pairs": pairs},
        explanation="",
    )
    return [row]


# ──────────────────────────────────────────────────────────────
# Паттерн Д — Переведи -> translate
# ──────────────────────────────────────────────────────────────


NUMBERED_DELIM_RE = re.compile(r"\d+\.\s+")


def _extract_numbered_items(lines: list) -> list:
    """Извлекает пронумерованные пункты "N. текст", устойчиво к тому, что
    несколько коротких пунктов иногда слиты PDF-типографикой в одну
    физическую строку (например: "1. 你几岁？ 2. 我九岁。 3. 多少钱？"), а сам
    текст пункта может содержать цифры ("Мне 18 лет.") — поэтому разбиение
    идёт по ПОЗИЦИЯМ разделителей "N. " (цифра-точка-пробел), а не по
    regex-классу "не цифра"."""
    body = " ".join(l.strip() for l in lines if l.strip())
    delims = list(NUMBERED_DELIM_RE.finditer(body))
    if not delims:
        return []
    items = []
    for i, m in enumerate(delims):
        start = m.end()
        end = delims[i + 1].start() if i + 1 < len(delims) else len(body)
        items.append(body[start:end].strip())
    return [i for i in items if i]


def parse_pattern_d(block: dict) -> list:
    title = block["title"]
    direction = "ru_to_zh" if title.startswith("Русский") else "zh_to_ru"

    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return None
    check_text = _get_check_text(block["lines"], check_idx)

    sources = _extract_numbered_items(block["lines"][:check_idx])
    if not sources:
        return None
    answers = _split_answers(check_text, len(sources))
    if len(answers) != len(sources):
        return None

    rows = []
    for src, ans in zip(sources, answers):
        if direction == "zh_to_ru":
            config = {"direction": "zh_to_ru", "source": src, "answer": ans}
        else:
            config = {"direction": "ru_to_zh", "source": src, "answer": ans}
        rows.append(
            ExerciseRow(
                type="translate",
                question_text=src,
                config=config,
                explanation="",
            )
        )
    return rows


# ──────────────────────────────────────────────────────────────
# Паттерн Г — Собери предложение -> build_word
# ──────────────────────────────────────────────────────────────


def parse_pattern_g_sentence(block: dict) -> list:
    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return None
    check_text = _get_check_text(block["lines"], check_idx)

    # Строки-задания часто слиты в одну физическую строку через "N. a / b / c",
    # несколько заданий на строке — поэтому ищем все "N. ...части через /..."
    # по всему объединённому телу до ✓.
    chunks = _extract_numbered_items(block["lines"][:check_idx])
    parts_list = [[p.strip() for p in chunk.split("/") if p.strip()] for chunk in chunks]

    if not parts_list:
        return None
    answers = _split_answers(check_text, len(parts_list))
    if len(answers) != len(parts_list):
        return None

    rows = []
    for parts, answer in zip(parts_list, answers):
        translation = SENTENCE_TRANSLATIONS.get(answer, "")
        rows.append(
            ExerciseRow(
                type="build_word",
                question_text="Соберите предложение из слов",
                config={"translation": translation, "parts": parts, "answer": answer},
                explanation="" if translation else f"(перевод не найден для: {answer!r})",
            )
        )
    return rows


# ──────────────────────────────────────────────────────────────
# Многовариантные вопросы (Паттерн А, Е, Ж и одноразовый «Г — Собери правило»)
# -> quiz / audio_quiz, диспетчеризуются по структуре (наличие "а)...б)...")
# ──────────────────────────────────────────────────────────────


def _extract_choice_items(lines: list, check_idx: int):
    """Проходит по строкам блока (до ✓) построчно, накапливая pending audio-тег
    и склеивая обёрнутые физические строки одного пункта, пока не встретит
    следующий пункт (audio-тег ИЛИ явную нумерацию с вариантами) либо конец.

    Возвращает список dict: {audio, stem, options: [str,...]}.
    """
    items = []
    pending_audio = None
    current_raw = None

    def flush():
        nonlocal current_raw
        if current_raw is None:
            return
        text = current_raw["text"].strip()
        markers = _find_option_markers(text)
        if not markers:
            current_raw = None
            return
        stem = text[: markers[0][0]].strip()
        stem = re.sub(r"^\d+\.\s*", "", stem).strip(" —:")
        options = []
        for i, (_start, m_end) in enumerate(markers):
            end = markers[i + 1][0] if i + 1 < len(markers) else len(text)
            options.append(text[m_end:end].strip())
        items.append({"audio": current_raw["audio"], "stem": stem, "options": options})
        current_raw = None

    for raw_line in lines[:check_idx]:
        line = raw_line.strip()
        if not line:
            continue
        audio_m = AUDIO_TAG_RE.fullmatch(line)
        if audio_m:
            flush()
            pending_audio = audio_m.group(1)
            continue
        starts_new_item = bool(NUMBERED_ITEM_START_RE.match(line)) or bool(
            bool(_find_option_markers(line)) and current_raw is None
        )
        if starts_new_item:
            flush()
            current_raw = {"audio": pending_audio, "text": line}
            pending_audio = None
        elif current_raw is not None:
            current_raw["text"] += " " + line
        # иначе — строка вне пункта (инструкция) игнорируется на этом этапе
    flush()
    return items


def _split_token_and_explanation(raw_token: str) -> tuple:
    """"г (не профессия)" -> ("г", "не профессия")
    "в (吗) 2)" -> при вызове raw_token уже не содержит след. "N)" (см. вызывающий код)
    "б — очень" -> ("б", "очень") — Ж/Е иногда используют "—" вместо скобок.
    Скобочная форма приоритетнее: значение до первой "(" — это ответ,
    содержимое скобок (до последней ")") — пояснение. Так безопаснее для
    случаев вида "不是 — отрицание, остальные — частицы", где внутри
    скобок есть свои тире.
    """
    raw_token = raw_token.strip()
    paren_idx = raw_token.find("(")
    if paren_idx != -1 and raw_token.rstrip().endswith(")"):
        answer = raw_token[:paren_idx].strip()
        explanation = raw_token[paren_idx + 1: raw_token.rstrip().rfind(")")].strip()
        return answer, explanation
    parts = re.split(r"\s*—\s*", raw_token, maxsplit=1)
    if len(parts) > 1:
        return parts[0].strip(), parts[1].strip()
    return raw_token, ""


def _match_answer_token_to_option(token: str, options: list):
    token_norm = token.strip()
    if token_norm in LETTER_TO_INDEX:
        return LETTER_TO_INDEX[token_norm]
    token_clean = _strip_paren_note(token_norm).strip().lower()
    for i, opt in enumerate(options):
        if opt.strip().lower() == token_clean:
            return i
    for i, opt in enumerate(options):
        if token_clean and (token_clean in opt.strip().lower() or opt.strip().lower() in token_clean):
            return i
    return None


def parse_choice_block(block: dict, exercise_type_hint: str = None) -> list:
    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return None
    check_text = _get_check_text(block["lines"], check_idx)

    items = _extract_choice_items(block["lines"], check_idx)
    if not items:
        return None

    # ✓-токены: "N) значение — пояснение" либо "N) значение" либо просто буквы подряд
    raw_tokens = _split_answers(check_text, len(items))
    if len(raw_tokens) != len(items):
        # fallback: возможно ответы без скобок-номеров, разделены пробелом (одни буквы)
        letters_only = re.findall(r"\b([абвг])\b", check_text)
        if len(letters_only) == len(items):
            raw_tokens = letters_only
        else:
            return None

    instruction = block["title"]
    # Первая строка тела, не являющаяся частью нумерованного пункта/аудио — общая инструкция
    for line in block["lines"][:check_idx]:
        s = line.strip()
        if not s:
            continue
        if AUDIO_TAG_RE.fullmatch(s) or NUMBERED_ITEM_START_RE.match(s) or _find_option_markers(s):
            break
        if not instruction:
            instruction = s
        else:
            sep = " " if instruction[-1] in ".!?:" else ". "
            instruction = instruction + sep + s

    has_audio = any(it["audio"] for it in items)
    ex_type = exercise_type_hint or ("audio_quiz" if has_audio else "quiz")

    rows = []
    for item, raw_token in zip(items, raw_tokens):
        answer_token, explanation = _split_token_and_explanation(raw_token)

        idx = _match_answer_token_to_option(answer_token, item["options"])
        if idx is None:
            return None  # не смогли сопоставить — блок целиком на ручную проверку

        question_text = item["stem"] or instruction or block["title"] or f"[{block['pattern_kind']}]"
        if ex_type == "audio_quiz":
            config = {"audio_url": item["audio"] or "", "options": item["options"], "correct": idx}
        else:
            config = {"options": item["options"], "correct": idx}
        rows.append(
            ExerciseRow(
                type=ex_type,
                question_text=question_text,
                config=config,
                explanation=explanation,
            )
        )
    return rows


# ──────────────────────────────────────────────────────────────
# Паттерн З — Тон на слух -> audio_quiz (открытый бланк -> 5 фиксированных
# вариантов "1"/"2"/"3"/"4"/"н")
# ──────────────────────────────────────────────────────────────

TONE_OPTIONS = ["1", "2", "3", "4", "н"]


def parse_pattern_z(block: dict) -> list:
    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return None
    check_text = _get_check_text(block["lines"], check_idx)

    audios = []
    pending_audio = None
    for raw_line in block["lines"][:check_idx]:
        line = raw_line.strip()
        if not line:
            continue
        audio_m = AUDIO_TAG_RE.fullmatch(line)
        if audio_m:
            pending_audio = audio_m.group(1)
            continue
        if NUMBERED_ITEM_START_RE.match(line) and pending_audio:
            audios.append(pending_audio)
            pending_audio = None

    if not audios:
        return None
    answers = _split_answers(check_text, len(audios))
    if len(answers) != len(audios):
        return None

    rows = []
    instruction = block["title"] or "Прослушайте и определите тон"
    for audio, ans in zip(audios, answers):
        ans_norm = ans.strip()
        idx = TONE_OPTIONS.index(ans_norm) if ans_norm in TONE_OPTIONS else None
        if idx is None:
            return None
        rows.append(
            ExerciseRow(
                type="audio_quiz",
                question_text=instruction,
                config={"audio_url": audio, "options": TONE_OPTIONS, "correct": idx},
                explanation="",
            )
        )
    return rows


# ──────────────────────────────────────────────────────────────
# Паттерн В (без вариантов) и Паттерн К -> fill_blank_open
# (в этом курсе НИ ОДИН блок «Паттерн В» не содержит вариантов а/б/в/г —
# см. docstring; поэтому В целиком идёт сюда же, отдельной ветки с
# fill_blank не потребовалось).
# ──────────────────────────────────────────────────────────────


BLANK_RUN_RE = re.compile(r"_{3,}")
CONSTANT_WORD_INSERT_RE = re.compile(r"^Вставьте\s+(\S+)\s+в нужное место")


def _extract_blank_values_for_line(line: str, raw_answer: str):
    """Одна строка-пункт (после нормализации содержит N меток "_____") и
    её "сырой" ✓-ответ -> список из N значений для этих меток.

    ✓-ответ в PDF встречается в двух видах:
      1) уже ГОТОВОЕ реконструированное предложение целиком (например,
         "我买了一本书。" для строки "我买 _____ 一本书 _____ 。") — тогда
         значения бланков находятся ДИФФОМ: сегменты строки-шаблона между
         метками ищутся по порядку внутри ответа, а между их вхождениями —
         и есть искомая вставка (может быть пустой строкой, если по
         грамматике блан следовало оставить пустым);
      2) сама вставка (одна на пробел-разделённые части, например
         "太 … 了" для строки с двумя метками) — используется, если
         диф не сработал (сегменты не нашлись как подстроки ответа).
    """
    # Для диффа нужна версия строки без русских пояснений в скобках
    # (например, "(я купил книгу)") — они не входят в китайский ✓-ответ и
    # иначе ломают поиск последнего сегмента. В итоговом template (в
    # вызывающем коде) подсказка остаётся — здесь она используется только
    # для поиска значений бланков.
    line_for_diff = re.sub(r"\([^)]*\)", "", line)
    segments = [s.strip() for s in line_for_diff.split("_____")]
    n_blanks = len(segments) - 1
    if n_blanks <= 0:
        return None

    pos = 0
    found_positions = []
    diff_ok = True
    for seg in segments:
        if not seg:
            found_positions.append(pos)
            continue
        idx = raw_answer.find(seg, pos)
        if idx == -1:
            diff_ok = False
            break
        found_positions.append(idx)
        pos = idx + len(seg)
    if diff_ok and len(found_positions) == len(segments):
        values = []
        for i in range(n_blanks):
            start = found_positions[i] + len(segments[i])
            end = found_positions[i + 1]
            values.append(_strip_paren_note(raw_answer[start:end].strip()))
        return values

    tokens = [t for t in raw_answer.replace("·", " ").split() if t not in ("…", "...")]
    if len(tokens) == n_blanks:
        return [_strip_paren_note(t) for t in tokens]
    if n_blanks == 1:
        return [_strip_paren_note(raw_answer.strip())]
    return None


def parse_fill_blank_open(block: dict) -> list:
    check_idx = _find_check_line_index(block["lines"])
    if check_idx == -1:
        return None
    check_text = _get_check_text(block["lines"], check_idx)

    raw_lines = [l.strip() for l in block["lines"][:check_idx] if l.strip()]
    # "Паттерн К" (диалог) — реплики уже разбиты по отдельным физическим
    # строкам вида "— ... _____ ...", каждая строка = один смысловой блок,
    # а ✓ даёт ПЛОСКИЙ список — один ответ на КАЖДЫЙ бланк по порядку
    # (независимо от того, сколько бланков в одной реплике).
    #
    # "Паттерн В" (нумерованные пункты) иногда сливает несколько коротких
    # пунктов "N. ..." в одну физическую строку — там нужно сначала
    # восстановить границы пунктов по номерам, а ✓ даёт один ответ на
    # КАЖДЫЙ ПУНКТ (в пункте может быть больше одного бланка — см.
    # _extract_blank_values_for_line).
    is_dialogue_style = any(l.startswith("—") for l in raw_lines if BLANK_RUN_RE.search(l))

    hint = block["title"]

    if is_dialogue_style:
        body_lines = []
        for line in raw_lines:
            if BLANK_RUN_RE.search(line):
                body_lines.append(line)
            elif not body_lines:
                hint = (hint + " " + line).strip() if hint else line
            else:
                body_lines[-1] += " " + line
        if not body_lines:
            return None
        body_lines = [BLANK_RUN_RE.sub("_____", l) for l in body_lines]

        total_blanks = sum(len(BLANK_RUN_RE.findall(l)) for l in body_lines)
        blanks = _split_answers(check_text, total_blanks)
        blanks = [_strip_paren_note(b) for b in blanks]
        if len(blanks) != total_blanks:
            return None
    else:
        lead = raw_lines[0] if raw_lines else ""
        if lead and not NUMBERED_ITEM_START_RE.match(lead) and not BLANK_RUN_RE.search(lead):
            hint = (hint + " " + lead).strip() if hint else lead
            raw_lines = raw_lines[1:]

        item_texts = _extract_numbered_items(raw_lines)
        body_lines = [BLANK_RUN_RE.sub("_____", t) for t in item_texts if BLANK_RUN_RE.search(t)]
        if not body_lines or len(body_lines) != len(item_texts):
            return None

        # Особый случай: "Вставьте 人 в нужное место" — в каждой строке ДВА
        # прочерка ("X + _____ = _______"), но по смыслу вставляется одно и
        # то же константное слово, а ✓ даёт не сами вставки, а готовые
        # составные слова (中国人 и т.п.) — их нельзя использовать как
        # значения бланков.
        const_m = CONSTANT_WORD_INSERT_RE.match(block["title"])
        if const_m:
            const_word = const_m.group(1)
            body_lines = [BLANK_RUN_RE.split(l, maxsplit=1)[0].rstrip(" +") + " + _____" for l in body_lines]
            blanks = [const_word] * len(body_lines)
        else:
            # ✓-строка даёт РОВНО один "N)"-ответ на каждый пункт (даже
            # если в нём несколько меток "_____").
            raw_answers = _split_answers(check_text, len(body_lines))
            if len(raw_answers) != len(body_lines):
                return None
            blanks = []
            for line, raw_ans in zip(body_lines, raw_answers):
                values = _extract_blank_values_for_line(line, raw_ans)
                if values is None:
                    return None
                blanks.extend(values)

    template = "\n".join(body_lines)
    blank_count = sum(len(BLANK_RUN_RE.findall(l)) for l in body_lines)
    if blank_count != len(blanks):
        return None

    row = ExerciseRow(
        type="fill_blank_open",
        question_text=hint or "Заполните пропуски",
        config={"template": template, "blanks": blanks, "hint": hint},
        explanation=f"Ответы: {' · '.join(v if v else '(пусто)' for v in blanks)}",
    )
    return [row]


# ──────────────────────────────────────────────────────────────
# Диспетчер по блоку
# ──────────────────────────────────────────────────────────────


def parse_block(block: dict, day: int = None):
    letter = block["pattern_letter"]
    kind = block["pattern_kind"]

    if letter == "Б":
        return parse_pattern_b(block, day=day)
    if letter == "Д":
        return parse_pattern_d(block)
    if letter == "Г" and "предложение" in kind:
        return parse_pattern_g_sentence(block)
    if letter == "Г" and "правило" in kind:
        return parse_choice_block(block)
    if letter in ("А", "Е", "Ж") and "ВСЕ" not in kind:
        return parse_choice_block(block)
    if letter == "З":
        return parse_pattern_z(block)
    if letter in ("В", "К"):
        return parse_fill_blank_open(block)
    return None  # неизвестный/особый паттерн (напр. «Выберите ВСЕ...») — на ручной разбор


# ──────────────────────────────────────────────────────────────
# Основной проход по PDF
# ──────────────────────────────────────────────────────────────


def parse_exercises(path: str) -> list:
    results = []
    with pdfplumber.open(path) as pdf:
        day_ranges = find_day_page_ranges(pdf)
        for day, start_page, end_page in day_ranges:
            if day in EXCLUDED_DAYS:
                continue
            section_text = extract_exercises_section(pdf, start_page, end_page)
            blocks = split_into_task_blocks(section_text)

            day_result = DayExercises(day=day)
            for block in blocks:
                rows = parse_block(block, day=day)
                if rows is None:
                    header = f"Задание {block['task_num']}. [Паттерн {block['pattern_letter']} — {block['pattern_kind']}] {block['title']}"
                    day_result.skipped.append(header + "\n" + "\n".join(block["lines"][:12]))
                    continue
                day_result.rows.extend(rows)
            results.append(day_result)
    return results


def print_stats(results: list):
    total_rows = 0
    total_skipped = 0
    type_counts = {}
    for d in results:
        total_rows += len(d.rows)
        total_skipped += len(d.skipped)
        for r in d.rows:
            type_counts[r.type] = type_counts.get(r.type, 0) + 1
        skip_note = f"  ⚠️ пропущено блоков: {len(d.skipped)}" if d.skipped else ""
        print(f"  День {d.day:>2}: упражнений={len(d.rows):>3}{skip_note}")
    print()
    print("По типам:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t:<16} {c}")
    print(f"\nИТОГО: {total_rows} упражнений, {total_skipped} блоков пропущено (см. --dump-json / --show-skipped)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf_path")
    parser.add_argument("--dump-json", metavar="PATH")
    parser.add_argument("--show-skipped", action="store_true")
    args = parser.parse_args()

    results = parse_exercises(args.pdf_path)
    print_stats(results)

    if args.show_skipped:
        for d in results:
            for s in d.skipped:
                print(f"\n--- День {d.day}, пропущенный блок ---")
                print(s)

    if args.dump_json:
        data = [
            {
                "day": d.day,
                "rows": [asdict(r) for r in d.rows],
                "skipped": d.skipped,
            }
            for d in results
        ]
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Сохранено: {args.dump_json}")


if __name__ == "__main__":
    main()
