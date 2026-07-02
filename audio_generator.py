import asyncio
import edge_tts
import boto3
import os
import re
from pypinyin import lazy_pinyin
from dotenv import load_dotenv
import os

load_dotenv()

VOICE = "zh-CN-XiaoxiaoNeural"
INPUT_FILE = "seed_content_new.py"
OUTPUT_FILE = "seed_content_new_with_audio.py"

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

FIND_PATTERN = re.compile(
    _KEY_AND_SEPARATOR + r'''["']([一-鿿]+)["']''',
    re.VERBOSE,
)


def build_replace_pattern(hanzi: str) -> re.Pattern:
    """Паттерн для точечной замены конкретного иероглифа-плейсхолдера на URL,
    с сохранением исходного текста ключа/оператора и стиля кавычек."""
    return re.compile(
        r'(' + _KEY_AND_SEPARATOR + r')(["\'])' + re.escape(hanzi) + r'\2',
        re.VERBOSE,
    )


def hanzi_to_filename(hanzi: str) -> str:
    """Конвертирует иероглифы в пиньинь для имени файла"""
    pinyin = lazy_pinyin(hanzi)
    return "_".join(pinyin) + ".mp3"


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


async def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # находим все иероглифы-плейсхолдеры в audio_url, независимо от контекста
    hanzi_list = FIND_PATTERN.findall(content)
    hanzi_list = list(set(hanzi_list))

    print(f"Найдено {len(hanzi_list)} уникальных иероглифов для генерации аудио")

    # генерируем все аудио
    replacements = {}
    for hanzi in hanzi_list:
        url = await generate_and_upload(hanzi)
        replacements[hanzi] = url

    # заменяем иероглифы на ссылки везде, где они встречаются как значение audio_url
    new_content = content
    for hanzi, url in replacements.items():
        pattern = build_replace_pattern(hanzi)
        new_content = pattern.sub(
            lambda m: m.group(1) + m.group(2) + url + m.group(2),
            new_content,
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n🎉 Готово! Новый файл сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
