import argparse
import asyncio
import os
import re

import boto3
import edge_tts
from dotenv import load_dotenv
from pypinyin import lazy_pinyin

load_dotenv()

VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_INPUT_FILE = "prod_db_scripts/seed_lessons_v2.py"

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_PUBLIC_URL = os.getenv('S3_PUBLIC_URL')

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

# Значение audio_url — строка из китайских иероглифов (плейсхолдер), встречающаяся
# в любом из следующих видов, независимо от контекста (словарь, присвоение и т.д.):
#   audio_url = "一石二鸟"          — обычное присвоение переменной
#   audio_url="一石二鸟"            — то же самое, без пробелов
#   "audio_url": "一石二鸟"         — значение в литерале словаря
#   idiom["audio_url"] = "一石二鸟"  — присвоение по ключу словаря (в т.ч. с одинарными кавычками)
_KEY_AND_SEPARATOR = r'''(?:
    ["']audio_url["']\s*:\s*        # "audio_url": ...      (словарь)
  | ["']audio_url["']\s*\]\s*=\s*   # x["audio_url"] = ...  (присвоение по ключу)
  | \baudio_url\s*=\s*              # audio_url = ...       (обычное присвоение)
)'''

AUDIO_URL_FIND_PATTERN = re.compile(
    _KEY_AND_SEPARATOR + r'''["']([一-鿿]+)["']''',
    re.VERBOSE,
)


def build_audio_url_replace_pattern(hanzi: str) -> re.Pattern:
    """Паттерн для точечной замены конкретного иероглифа-плейсхолдера на URL,
    с сохранением исходного текста ключа/оператора и стиля кавычек."""
    return re.compile(
        r'(' + _KEY_AND_SEPARATOR + r')(["\'])' + re.escape(hanzi) + r'\2',
        re.VERBOSE,
    )


# data-audio="..." — атрибут реплики диалога в HTML внутри content_html
# (см. prod_db_scripts/seed_lessons_v2.py, функция dialogue()). В отличие от
# audio_url, значение здесь — это иероглифы ЦЕЛИКОМ, вместе с китайской
# пунктуацией (？！。，), поэтому символьный класс шире, чем у audio_url.
# Лукахед требует хотя бы один иероглиф CJK внутри значения — это делает
# паттерн безопасным для повторного запуска на уже обработанном файле
# (URL-значения без иероглифов не заматчатся).
DATA_AUDIO_FIND_PATTERN = re.compile(
    r'data-audio=(["\'])(?=[^"\']*[一-鿿])([^"\']+)\1'
)


def build_data_audio_replace_pattern(hanzi: str) -> re.Pattern:
    return re.compile(
        r'(data-audio=)(["\'])' + re.escape(hanzi) + r'\2'
    )


def _looks_like_helper_based_module(content: str) -> bool:
    """seed_lessons_v2.py (в отличие от seed_lessons.py / seed_idioms.py и т.п.)
    собирает content_html HTML-хелперами (dialogue(), build()...) при импорте
    модуля — поэтому в исходном ТЕКСТЕ файла реальных data-audio="汉字" нет,
    там только f-строка-шаблон data-audio="{hanzi}" внутри тела dialogue().
    Такой файл нужно сначала импортировать и развернуть в литеральный текст
    (см. render_helper_based_module), иначе текстовый regex ничего не найдёт."""
    return "LESSONS_DATA_V2" in content and "def dialogue(" in content


def render_helper_based_module(module_path: str) -> str:
    """Импортирует seed-модуль, собранный HTML-хелперами, и сериализует его
    LESSONS_DATA_V2 в плоский текст с уже вычисленным content_html (репры
    строк корректно экранируют кавычки/переносы — результат гарантированно
    валиден как Python). После этого data-audio="<реальные иероглифы>" в нём
    можно искать и заменять тем же текстовым regex, что и для обычных
    seed-файлов."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("_seed_module_for_audio", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    lines = [
        '"""Развёрнутая версия seed-модуля (сгенерировано audio_generator.py '
        "из исходника, где content_html собирается HTML-хелперами "
        'dialogue()/build()/table()). Здесь content_html — уже готовые '
        'литеральные строки."""\n\n',
        "LESSONS_DATA_V2 = [\n",
    ]
    for day, name, content_html in module.LESSONS_DATA_V2:
        lines.append(f"    ({day!r}, {name!r}, {content_html!r}),\n")
    lines.append("]\n")
    return "".join(lines)


def hanzi_to_filename(hanzi: str) -> str:
    """Конвертирует иероглифы в пиньинь для имени файла.

    Реплики диалогов (data-audio) могут содержать китайскую пунктуацию
    (？！。，) — pypinyin возвращает такие символы как отдельные "слоги" без
    изменений, поэтому для имени файла они отфильтровываются (в S3-ключе
    им не место), а сам текст ПОЛНОСТЬЮ (с пунктуацией) уходит в TTS —
    это даёт более естественные паузы и интонацию.
    """
    pinyin = lazy_pinyin(hanzi)
    clean = [syllable for syllable in pinyin if re.fullmatch(r'[a-zA-Z0-9]+', syllable)]
    return "_".join(clean) + ".mp3"


async def generate_and_upload(hanzi: str) -> str:
    """Генерирует аудио и загружает в S3"""
    filename = hanzi_to_filename(hanzi)
    tmp_path = f"/tmp/{filename}"
    public_url = f"{S3_PUBLIC_URL}/{filename}"

    # проверяем есть ли уже в S3
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=filename)
        print(f"   ⏭ {hanzi} ({filename}) — уже есть в S3")
        return public_url
    except Exception:
        pass

    # генерируем аудио
    await edge_tts.Communicate(hanzi, VOICE).save(tmp_path)

    # загружаем в S3
    s3.upload_file(
        tmp_path,
        S3_BUCKET,
        filename,
        ExtraArgs={"ContentType": "audio/mpeg", "ACL": "public-read"}
    )
    os.remove(tmp_path)
    print(f"   ✅ {hanzi} → {public_url}")
    return public_url


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Генерирует аудио (edge-tts) для иероглифов-плейсхолдеров, найденных "
            "в audio_url (словари/присвоения) и data-audio (реплики диалогов в "
            "content_html), загружает их в S3 и заменяет плейсхолдеры на ссылки "
            "в копии файла."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_INPUT_FILE,
        help=f"Путь к исходному seed-файлу (по умолчанию: {DEFAULT_INPUT_FILE})",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Путь для сохранения результата (по умолчанию: <input>_with_audio.py)",
    )
    args = parser.parse_args()
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_with_audio{ext}"
    return args


async def main():
    args = parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    if _looks_like_helper_based_module(content):
        print(
            "ℹ️  Файл собирает content_html через HTML-хелперы (dialogue()/build()) — "
            "импортирую модуль и разворачиваю LESSONS_DATA_V2 в литеральные строки "
            "перед поиском data-audio."
        )
        content = render_helper_based_module(args.input)

    # находим все иероглифы-плейсхолдеры: и в audio_url, и в data-audio
    audio_url_hanzi = set(AUDIO_URL_FIND_PATTERN.findall(content))
    data_audio_hanzi = {m[1] for m in DATA_AUDIO_FIND_PATTERN.findall(content)}
    hanzi_list = sorted(audio_url_hanzi | data_audio_hanzi)

    print(
        f"Найдено {len(hanzi_list)} уникальных иероглифов для генерации аудио "
        f"(audio_url: {len(audio_url_hanzi)}, data-audio: {len(data_audio_hanzi)})"
    )

    # генерируем все аудио
    replacements = {}
    for hanzi in hanzi_list:
        url = await generate_and_upload(hanzi)
        replacements[hanzi] = url

    # заменяем иероглифы на ссылки везде, где они встречаются как значение
    # audio_url или data-audio
    new_content = content
    for hanzi, url in replacements.items():
        if hanzi in audio_url_hanzi:
            pattern = build_audio_url_replace_pattern(hanzi)
            new_content = pattern.sub(
                lambda m: m.group(1) + m.group(2) + url + m.group(2),
                new_content,
            )
        if hanzi in data_audio_hanzi:
            pattern = build_data_audio_replace_pattern(hanzi)
            new_content = pattern.sub(
                lambda m: m.group(1) + m.group(2) + url + m.group(2),
                new_content,
            )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n🎉 Готово! Новый файл сохранён: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
