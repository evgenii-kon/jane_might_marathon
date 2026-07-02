"""
Seed script: 5 текстов HSK-1 с вопросами на понимание.
Идемпотентный — повторный запуск не дублирует данные (проверяет по slug).
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "bndcn34894hcn289",
    "dbname": "fastapi_db",
}

# ────────────────────────────────────────────────────────────────
# Тексты и вопросы
# ────────────────────────────────────────────────────────────────
READING_DATA = [
    {
        "slug": "znakomstvo",
        "title": "Знакомство",
        "description": "Приветствие, имя и откуда родом",
        "hsk_level": "HSK-1",
        "content_hanzi": (
            "你好！我叫李明。\n"
            "我是中国人。\n"
            "我住在北京。\n"
            "你叫什么名字？\n"
            "我叫王芳。\n"
            "你是哪国人？\n"
            "我是俄罗斯人。\n"
            "我住在莫斯科。\n"
            "认识你很高兴！\n"
            "我也很高兴认识你。"
        ),
        "content_pinyin": (
            "Nǐ hǎo! Wǒ jiào Lǐ Míng.\n"
            "Wǒ shì Zhōngguó rén.\n"
            "Wǒ zhù zài Běijīng.\n"
            "Nǐ jiào shénme míngzi?\n"
            "Wǒ jiào Wáng Fāng.\n"
            "Nǐ shì nǎ guó rén?\n"
            "Wǒ shì Éluósī rén.\n"
            "Wǒ zhù zài Mòsīkē.\n"
            "Rènshi nǐ hěn gāoxìng!\n"
            "Wǒ yě hěn gāoxìng rènshi nǐ."
        ),
        "content_translation": (
            "Привет! Меня зовут Ли Мин.\n"
            "Я китаец.\n"
            "Я живу в Пекине.\n"
            "Как тебя зовут?\n"
            "Меня зовут Ван Фан.\n"
            "Ты из какой страны?\n"
            "Я русская.\n"
            "Я живу в Москве.\n"
            "Рада познакомиться!\n"
            "Я тоже очень рад познакомиться с тобой."
        ),
        "questions": [
            {
                "order": 0,
                "question": "Как зовут первого человека в тексте?",
                "option_1": "王芳",
                "option_2": "李明",
                "option_3": "张伟",
                "option_4": "刘洋",
                "correct_answer": 2,
                "explanation": "В первом предложении: 我叫李明 — Меня зовут Ли Мин.",
            },
            {
                "order": 1,
                "question": "Откуда Ли Мин?",
                "option_1": "Из Москвы",
                "option_2": "Из Шанхая",
                "option_3": "Из Пекина",
                "option_4": "Из Токио",
                "correct_answer": 3,
                "explanation": "我住在北京 — Я живу в Пекине.",
            },
            {
                "order": 2,
                "question": "Как зовут второго персонажа?",
                "option_1": "李明",
                "option_2": "张华",
                "option_3": "王芳",
                "option_4": "陈刚",
                "correct_answer": 3,
                "explanation": "我叫王芳 — Меня зовут Ван Фан.",
            },
            {
                "order": 3,
                "question": "Откуда Ван Фан?",
                "option_1": "Из Китая",
                "option_2": "Из России",
                "option_3": "Из Японии",
                "option_4": "Из Кореи",
                "correct_answer": 2,
                "explanation": "我是俄罗斯人 — Я русская.",
            },
            {
                "order": 4,
                "question": "Где живёт Ван Фан?",
                "option_1": "В Пекине",
                "option_2": "В Шанхае",
                "option_3": "В Москве",
                "option_4": "В Лондоне",
                "correct_answer": 3,
                "explanation": "我住在莫斯科 — Я живу в Москве.",
            },
        ],
    },
    {
        "slug": "v-kafe",
        "title": "В кафе",
        "description": "Заказ еды и напитков",
        "hsk_level": "HSK-1",
        "content_hanzi": (
            "我想喝水。\n"
            "服务员，请来一杯茶。\n"
            "你们有咖啡吗？\n"
            "有，我们有咖啡。\n"
            "我要一杯咖啡，不要糖。\n"
            "你要吃什么？\n"
            "我要米饭和鸡蛋。\n"
            "这个多少钱？\n"
            "十五块钱。\n"
            "好，谢谢！"
        ),
        "content_pinyin": (
            "Wǒ xiǎng hē shuǐ.\n"
            "Fúwùyuán, qǐng lái yī bēi chá.\n"
            "Nǐmen yǒu kāfēi ma?\n"
            "Yǒu, wǒmen yǒu kāfēi.\n"
            "Wǒ yào yī bēi kāfēi, bù yào táng.\n"
            "Nǐ yào chī shénme?\n"
            "Wǒ yào mǐfàn hé jīdàn.\n"
            "Zhège duōshao qián?\n"
            "Shíwǔ kuài qián.\n"
            "Hǎo, xièxie!"
        ),
        "content_translation": (
            "Я хочу воды.\n"
            "Официант, пожалуйста, один чай.\n"
            "У вас есть кофе?\n"
            "Да, у нас есть кофе.\n"
            "Мне один кофе, без сахара.\n"
            "Что вы будете есть?\n"
            "Мне рис и яйца.\n"
            "Сколько это стоит?\n"
            "Пятнадцать юаней.\n"
            "Хорошо, спасибо!"
        ),
        "questions": [
            {
                "order": 0,
                "question": "Что хочет выпить посетитель в начале текста?",
                "option_1": "Кофе",
                "option_2": "Чай",
                "option_3": "Воду",
                "option_4": "Сок",
                "correct_answer": 3,
                "explanation": "我想喝水 — Я хочу воды.",
            },
            {
                "order": 1,
                "question": "Есть ли в кафе кофе?",
                "option_1": "Нет",
                "option_2": "Только по утрам",
                "option_3": "Да",
                "option_4": "Не знают",
                "correct_answer": 3,
                "explanation": "有，我们有咖啡 — Да, у нас есть кофе.",
            },
            {
                "order": 2,
                "question": "Как посетитель хочет кофе?",
                "option_1": "С молоком",
                "option_2": "Без сахара",
                "option_3": "С сахаром",
                "option_4": "Без молока",
                "correct_answer": 2,
                "explanation": "不要糖 — без сахара.",
            },
            {
                "order": 3,
                "question": "Что заказывает посетитель из еды?",
                "option_1": "Суп и хлеб",
                "option_2": "Лапшу и курицу",
                "option_3": "Рис и яйца",
                "option_4": "Рыбу и рис",
                "correct_answer": 3,
                "explanation": "我要米饭和鸡蛋 — Мне рис и яйца.",
            },
            {
                "order": 4,
                "question": "Сколько стоит заказ?",
                "option_1": "5 юаней",
                "option_2": "50 юаней",
                "option_3": "15 юаней",
                "option_4": "51 юань",
                "correct_answer": 3,
                "explanation": "十五块钱 — Пятнадцать юаней.",
            },
        ],
    },
    {
        "slug": "moya-semya",
        "title": "Моя семья",
        "description": "Описание семьи на китайском",
        "hsk_level": "HSK-1",
        "content_hanzi": (
            "我家有五口人。\n"
            "爸爸、妈妈、哥哥、妹妹和我。\n"
            "我爸爸是医生。\n"
            "我妈妈是老师。\n"
            "我哥哥在大学学习。\n"
            "我妹妹很小，她五岁。\n"
            "我们住在一起。\n"
            "我很爱我的家人。\n"
            "我们家很幸福。"
        ),
        "content_pinyin": (
            "Wǒ jiā yǒu wǔ kǒu rén.\n"
            "Bàba, māma, gēge, mèimei hé wǒ.\n"
            "Wǒ bàba shì yīshēng.\n"
            "Wǒ māma shì lǎoshī.\n"
            "Wǒ gēge zài dàxué xuéxí.\n"
            "Wǒ mèimei hěn xiǎo, tā wǔ suì.\n"
            "Wǒmen zhù zài yīqǐ.\n"
            "Wǒ hěn ài wǒde jiārén.\n"
            "Wǒmen jiā hěn xìngfú."
        ),
        "content_translation": (
            "В моей семье пять человек.\n"
            "Папа, мама, старший брат, младшая сестра и я.\n"
            "Мой папа — врач.\n"
            "Моя мама — учительница.\n"
            "Мой старший брат учится в университете.\n"
            "Моя младшая сестра очень маленькая, ей пять лет.\n"
            "Мы живём вместе.\n"
            "Я очень люблю свою семью.\n"
            "Наша семья очень счастливая."
        ),
        "questions": [
            {
                "order": 0,
                "question": "Сколько человек в семье автора?",
                "option_1": "3",
                "option_2": "4",
                "option_3": "5",
                "option_4": "6",
                "correct_answer": 3,
                "explanation": "我家有五口人 — В моей семье пять человек.",
            },
            {
                "order": 1,
                "question": "Кем работает папа?",
                "option_1": "Учителем",
                "option_2": "Врачом",
                "option_3": "Инженером",
                "option_4": "Водителем",
                "correct_answer": 2,
                "explanation": "我爸爸是医生 — Мой папа — врач.",
            },
            {
                "order": 2,
                "question": "Где учится старший брат?",
                "option_1": "В школе",
                "option_2": "Дома",
                "option_3": "В университете",
                "option_4": "В колледже",
                "correct_answer": 3,
                "explanation": "在大学学习 — учится в университете.",
            },
            {
                "order": 3,
                "question": "Сколько лет младшей сестре?",
                "option_1": "3 года",
                "option_2": "7 лет",
                "option_3": "5 лет",
                "option_4": "10 лет",
                "correct_answer": 3,
                "explanation": "她五岁 — ей пять лет.",
            },
            {
                "order": 4,
                "question": "Как автор описывает свою семью?",
                "option_1": "Шумной",
                "option_2": "Большой",
                "option_3": "Счастливой",
                "option_4": "Весёлой",
                "correct_answer": 3,
                "explanation": "我们家很幸福 — Наша семья очень счастливая.",
            },
            {
                "order": 5,
                "question": "Кем работает мама?",
                "option_1": "Врачом",
                "option_2": "Учительницей",
                "option_3": "Поваром",
                "option_4": "Продавцом",
                "correct_answer": 2,
                "explanation": "我妈妈是老师 — Моя мама — учительница.",
            },
        ],
    },
    {
        "slug": "moy-den",
        "title": "Мой день",
        "description": "Распорядок дня",
        "hsk_level": "HSK-1",
        "content_hanzi": (
            "我每天七点起床。\n"
            "我先喝水，然后吃早饭。\n"
            "早饭我吃鸡蛋和米饭。\n"
            "八点我去学校。\n"
            "我在学校学习汉语。\n"
            "十二点我吃午饭。\n"
            "下午我看书。\n"
            "晚上我看电视。\n"
            "我十点睡觉。\n"
            "我喜欢这样的生活。"
        ),
        "content_pinyin": (
            "Wǒ měitiān qī diǎn qǐchuáng.\n"
            "Wǒ xiān hē shuǐ, rán hòu chī zǎofàn.\n"
            "Zǎofàn wǒ chī jīdàn hé mǐfàn.\n"
            "Bā diǎn wǒ qù xuéxiào.\n"
            "Wǒ zài xuéxiào xuéxí Hànyǔ.\n"
            "Shí'èr diǎn wǒ chī wǔfàn.\n"
            "Xiàwǔ wǒ kàn shū.\n"
            "Wǎnshang wǒ kàn diànshì.\n"
            "Wǒ shí diǎn shuìjiào.\n"
            "Wǒ xǐhuān zhèyàng de shēnghuó."
        ),
        "content_translation": (
            "Каждый день я встаю в семь часов.\n"
            "Сначала пью воду, потом завтракаю.\n"
            "На завтрак я ем яйца и рис.\n"
            "В восемь часов иду в школу.\n"
            "В школе я учу китайский язык.\n"
            "В двенадцать часов обедаю.\n"
            "Днём читаю книги.\n"
            "Вечером смотрю телевизор.\n"
            "Ложусь спать в десять часов.\n"
            "Мне нравится такой распорядок."
        ),
        "questions": [
            {
                "order": 0,
                "question": "Во сколько автор встаёт?",
                "option_1": "В 6:00",
                "option_2": "В 8:00",
                "option_3": "В 7:00",
                "option_4": "В 9:00",
                "correct_answer": 3,
                "explanation": "七点起床 — встаёт в семь часов.",
            },
            {
                "order": 1,
                "question": "Что автор ест на завтрак?",
                "option_1": "Суп и хлеб",
                "option_2": "Яйца и рис",
                "option_3": "Лапшу",
                "option_4": "Фрукты",
                "correct_answer": 2,
                "explanation": "鸡蛋和米饭 — яйца и рис.",
            },
            {
                "order": 2,
                "question": "Что автор изучает в школе?",
                "option_1": "Математику",
                "option_2": "Английский",
                "option_3": "Китайский язык",
                "option_4": "Историю",
                "correct_answer": 3,
                "explanation": "学习汉语 — учит китайский язык.",
            },
            {
                "order": 3,
                "question": "Что делает автор днём после школы?",
                "option_1": "Смотрит телевизор",
                "option_2": "Гуляет",
                "option_3": "Читает книги",
                "option_4": "Спит",
                "correct_answer": 3,
                "explanation": "下午我看书 — Днём читаю книги.",
            },
            {
                "order": 4,
                "question": "Во сколько автор ложится спать?",
                "option_1": "В 9:00",
                "option_2": "В 11:00",
                "option_3": "В 10:00",
                "option_4": "В 12:00",
                "correct_answer": 3,
                "explanation": "十点睡觉 — ложится спать в десять.",
            },
            {
                "order": 5,
                "question": "Что делает автор вечером?",
                "option_1": "Читает",
                "option_2": "Смотрит телевизор",
                "option_3": "Занимается спортом",
                "option_4": "Готовит еду",
                "correct_answer": 2,
                "explanation": "晚上我看电视 — Вечером смотрю телевизор.",
            },
        ],
    },
    {
        "slug": "v-magazine",
        "title": "В магазине",
        "description": "Покупки и цены",
        "hsk_level": "HSK-1",
        "content_hanzi": (
            "我去超市买东西。\n"
            "我要买水果和水。\n"
            "苹果多少钱一斤？\n"
            "三块钱一斤。\n"
            "我要两斤苹果。\n"
            "还有什么？\n"
            "我还要一瓶水。\n"
            "水多少钱？\n"
            "两块钱一瓶。\n"
            "一共八块钱。\n"
            "我用手机付钱。\n"
            "谢谢，再见！"
        ),
        "content_pinyin": (
            "Wǒ qù chāoshì mǎi dōngxi.\n"
            "Wǒ yào mǎi shuǐguǒ hé shuǐ.\n"
            "Píngguǒ duōshao qián yī jīn?\n"
            "Sān kuài qián yī jīn.\n"
            "Wǒ yào liǎng jīn píngguǒ.\n"
            "Hái yǒu shénme?\n"
            "Wǒ hái yào yī píng shuǐ.\n"
            "Shuǐ duōshao qián?\n"
            "Liǎng kuài qián yī píng.\n"
            "Yīgòng bā kuài qián.\n"
            "Wǒ yòng shǒujī fù qián.\n"
            "Xièxie, zàijiàn!"
        ),
        "content_translation": (
            "Я иду в супермаркет за покупками.\n"
            "Мне нужно купить фрукты и воду.\n"
            "Сколько стоят яблоки за цзинь?\n"
            "Три юаня за цзинь.\n"
            "Мне два цзиня яблок.\n"
            "Что ещё?\n"
            "Мне ещё одна бутылка воды.\n"
            "Сколько стоит вода?\n"
            "Два юаня за бутылку.\n"
            "Итого восемь юаней.\n"
            "Я плачу телефоном.\n"
            "Спасибо, до свидания!"
        ),
        "questions": [
            {
                "order": 0,
                "question": "Куда идёт покупатель?",
                "option_1": "На рынок",
                "option_2": "В ресторан",
                "option_3": "В супермаркет",
                "option_4": "В аптеку",
                "correct_answer": 3,
                "explanation": "我去超市 — Я иду в супермаркет.",
            },
            {
                "order": 1,
                "question": "Что хочет купить покупатель?",
                "option_1": "Мясо и хлеб",
                "option_2": "Фрукты и воду",
                "option_3": "Рис и яйца",
                "option_4": "Чай и кофе",
                "correct_answer": 2,
                "explanation": "我要买水果和水 — Мне нужно купить фрукты и воду.",
            },
            {
                "order": 2,
                "question": "Сколько стоят яблоки?",
                "option_1": "2 юаня за цзинь",
                "option_2": "5 юаней за цзинь",
                "option_3": "3 юаня за цзинь",
                "option_4": "10 юаней за цзинь",
                "correct_answer": 3,
                "explanation": "三块钱一斤 — три юаня за цзинь.",
            },
            {
                "order": 3,
                "question": "Сколько яблок берёт покупатель?",
                "option_1": "1 цзинь",
                "option_2": "3 цзиня",
                "option_3": "2 цзиня",
                "option_4": "5 цзиней",
                "correct_answer": 3,
                "explanation": "我要两斤苹果 — Мне два цзиня яблок.",
            },
            {
                "order": 4,
                "question": "Сколько стоит вода?",
                "option_1": "1 юань",
                "option_2": "2 юаня",
                "option_3": "3 юаня",
                "option_4": "5 юаней",
                "correct_answer": 2,
                "explanation": "两块钱一瓶 — два юаня за бутылку.",
            },
            {
                "order": 5,
                "question": "Сколько покупатель заплатил в итоге?",
                "option_1": "5 юаней",
                "option_2": "10 юаней",
                "option_3": "8 юаней",
                "option_4": "6 юаней",
                "correct_answer": 3,
                "explanation": "一共八块钱 — Итого восемь юаней.",
            },
            {
                "order": 6,
                "question": "Как покупатель расплатился?",
                "option_1": "Наличными",
                "option_2": "Картой",
                "option_3": "Телефоном",
                "option_4": "Чеком",
                "correct_answer": 3,
                "explanation": "用手机付钱 — плачу телефоном.",
            },
        ],
    },
]


def run():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for item in READING_DATA:
        # Проверяем, существует ли текст с таким slug
        cur.execute("SELECT id FROM reading_texts WHERE slug = %s", (item["slug"],))
        row = cur.fetchone()
        if row:
            print(f"  Пропускаем '{item['title']}' (slug уже существует)")
            continue

        cur.execute(
            """
            INSERT INTO reading_texts
                (title, slug, description, content_hanzi, content_pinyin, content_translation, hsk_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                item["title"],
                item["slug"],
                item["description"],
                item["content_hanzi"],
                item["content_pinyin"],
                item["content_translation"],
                item["hsk_level"],
            ),
        )
        text_id = cur.fetchone()[0]
        print(f"  Создан текст '{item['title']}' (id={text_id})")

        for q in item["questions"]:
            cur.execute(
                """
                INSERT INTO reading_questions
                    (text_id, question, option_1, option_2, option_3, option_4,
                     correct_answer, explanation, order_in_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    text_id,
                    q["question"],
                    q["option_1"],
                    q["option_2"],
                    q["option_3"],
                    q["option_4"],
                    q["correct_answer"],
                    q.get("explanation"),
                    q["order"],
                ),
            )
        print(f"    Добавлено {len(item['questions'])} вопросов")

    conn.commit()
    cur.close()
    conn.close()
    print("\nГотово!")


if __name__ == "__main__":
    run()
