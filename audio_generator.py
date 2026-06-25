import asyncio
import edge_tts
import boto3
import os
import re
from pypinyin import lazy_pinyin

VOICE = "zh-CN-XiaoxiaoNeural"
INPUT_FILE = "seed_content.py"
OUTPUT_FILE = "seed_content_with_audio.py"

S3_ENDPOINT = "https://s3.selcdn.ru"
S3_ACCESS_KEY = "твой_ключ"
S3_SECRET_KEY = "твой_секрет"
S3_BUCKET = "твой_бакет"
S3_PUBLIC_URL = "https://твой_бакет.selstorage.ru"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
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
    except:
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

    # находим все иероглифы в audio_url
    hanzi_list = re.findall(r'audio_url\s*=\s*["\']+([\u4e00-\u9fff]+)["\']', content)
    hanzi_list = list(set(hanzi_list))

    print(f"Найдено {len(hanzi_list)} уникальных иероглифов для генерации аудио")

    # генерируем все аудио
    replacements = {}
    for hanzi in hanzi_list:
        url = await generate_and_upload(hanzi)
        replacements[hanzi] = url

    # заменяем иероглифы на ссылки
    new_content = content
    for hanzi, url in replacements.items():
        new_content = re.sub(
            rf'(audio_url\s*=\s*["\']){re.escape(hanzi)}(["\'])',
            rf'\g<1>{url}\2',
            new_content
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n🎉 Готово! Новый файл сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())