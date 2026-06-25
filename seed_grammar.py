"""
Seed script: наполняет БД правилами грамматики китайского языка HSK-1.
Идемпотентный — повторный запуск не дублирует данные.
Использует psycopg2 напрямую.
"""

import os
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "bndcn34894hcn289"),
    "dbname": os.getenv("DB_NAME", "fastapi_db"),
}

# ──────────────────────────────────────────────────────────────
# ТЕГИ
# ──────────────────────────────────────────────────────────────
TAGS = [
    ("Структура предложения", "struktura-predlozheniya"),
    ("Частицы", "chastitsy"),
    ("Глаголы", "glagoly"),
    ("Отрицание", "otritsanie"),
    ("Вопросы", "voprosy"),
    ("Местоимения", "mestoimeniya"),
    ("Числа и счёт", "chisla-i-schyot"),
    ("Время", "vremya"),
    ("Прилагательные", "prilagatelnyye"),
]

# ──────────────────────────────────────────────────────────────
# ПРАВИЛА ГРАММАТИКИ
# Формат: (title, slug, description, content_html, hsk_level, [tag_slugs])
# ──────────────────────────────────────────────────────────────
RULES = [
    (
        "Структура предложения: Подлежащее + Сказуемое + Дополнение (S+V+O)",
        "s-v-o-struktura",
        "Базовый порядок слов в китайском предложении — S+V+O, как и в русском, но без изменений по падежам.",
        """<h2>Структура предложения: S + V + O</h2>
<p>Китайский язык использует строгий порядок слов. Базовая структура: <strong>подлежащее + сказуемое + дополнение</strong>, точно как в русском языке, но без склонений и спряжений.</p>

<h3>Схема</h3>
<p><strong>S</strong> (кто?) + <strong>V</strong> (что делает?) + <strong>O</strong> (что/кого?)</p>

<h3>Примеры</h3>
<table>
  <tr><th>Китайский</th><th>Пиньинь</th><th>Перевод</th></tr>
  <tr><td><strong>我</strong>吃<strong>饭</strong>。</td><td>Wǒ chī fàn.</td><td>Я ем рис.</td></tr>
  <tr><td><strong>她</strong>学<strong>中文</strong>。</td><td>Tā xué Zhōngwén.</td><td>Она учит китайский.</td></tr>
  <tr><td><strong>他们</strong>看<strong>电影</strong>。</td><td>Tāmen kàn diànyǐng.</td><td>Они смотрят кино.</td></tr>
  <tr><td><strong>我</strong>喜欢<strong>音乐</strong>。</td><td>Wǒ xǐhuān yīnyuè.</td><td>Я люблю музыку.</td></tr>
</table>

<h3>Важно</h3>
<ul>
  <li>В китайском глагол <strong>не спрягается</strong> по лицам и числам: 我吃、你吃、他吃 — везде 吃.</li>
  <li>Нет падежей: 我 (я) не меняется на «меня» или «мне».</li>
  <li>Порядок слов менять нельзя — это единственный способ показать роль слова в предложении.</li>
</ul>

<h3>Диалог</h3>
<p><strong>A:</strong> 你做什么？(Nǐ zuò shénme?) — Что ты делаешь?<br>
<strong>B:</strong> 我看书。(Wǒ kàn shū.) — Я читаю книгу.<br>
<strong>A:</strong> 你喜欢看书吗？(Nǐ xǐhuān kàn shū ma?) — Ты любишь читать?<br>
<strong>B:</strong> 我很喜欢！(Wǒ hěn xǐhuān!) — Очень люблю!</p>""",
        "HSK-1",
        ["struktura-predlozheniya", "glagoly"],
    ),
    (
        "Глагол-связка 是 (shì) — «быть, являться»",
        "glagol-shi",
        "Глагол 是 (shì) соединяет подлежащее с существительным или именной частью сказуемого.",
        """<h2>Глагол-связка 是 (shì)</h2>
<p>В китайском языке 是 (shì) — «быть, являться» — используется для отождествления: «X является Y».</p>

<h3>Структура</h3>
<p><strong>A + 是 + B</strong> — «A является B»</p>

<h3>Примеры</h3>
<table>
  <tr><th>Китайский</th><th>Пиньинь</th><th>Перевод</th></tr>
  <tr><td>我<strong>是</strong>学生。</td><td>Wǒ shì xuésheng.</td><td>Я (являюсь) студент.</td></tr>
  <tr><td>她<strong>是</strong>老师。</td><td>Tā shì lǎoshī.</td><td>Она учитель.</td></tr>
  <tr><td>这<strong>是</strong>书。</td><td>Zhè shì shū.</td><td>Это книга.</td></tr>
  <tr><td>他<strong>是</strong>中国人。</td><td>Tā shì Zhōngguórén.</td><td>Он китаец.</td></tr>
</table>

<h3>Отрицание: 不是 (bù shì)</h3>
<p>Перед 是 ставится 不 для отрицания:</p>
<ul>
  <li>我<strong>不是</strong>老师。— Я не учитель.</li>
  <li>这<strong>不是</strong>我的书。— Это не моя книга.</li>
</ul>

<h3>Вопрос: 是...吗？ или 是不是？</h3>
<ul>
  <li>你是学生<strong>吗</strong>？— Ты студент?</li>
  <li>你<strong>是不是</strong>老师？— Ты учитель или нет?</li>
</ul>

<h3>Важно</h3>
<p>С <strong>прилагательными</strong> 是 не нужен! Не говорят 我是好 (неверно). Правильно: 我很好 (Мне хорошо). 是 используется только с <em>существительными</em>.</p>""",
        "HSK-1",
        ["struktura-predlozheniya", "glagoly"],
    ),
    (
        "Конструкция 有 (yǒu) — «иметь, есть в наличии»",
        "glagol-you",
        "Глагол 有 (yǒu) используется для выражения обладания и существования.",
        """<h2>Конструкция 有 (yǒu) — «иметь / есть»</h2>
<p>有 (yǒu) выполняет две роли: <strong>обладание</strong> («у меня есть») и <strong>существование</strong> («там есть»).</p>

<h3>1. Обладание: «У меня есть X»</h3>
<p>Структура: <strong>人 + 有 + 东西</strong></p>
<table>
  <tr><th>Китайский</th><th>Пиньинь</th><th>Перевод</th></tr>
  <tr><td>我<strong>有</strong>一本书。</td><td>Wǒ yǒu yī běn shū.</td><td>У меня есть книга.</td></tr>
  <tr><td>她<strong>有</strong>一个弟弟。</td><td>Tā yǒu yīgè dìdi.</td><td>У неё есть младший брат.</td></tr>
  <tr><td>你<strong>有</strong>时间吗？</td><td>Nǐ yǒu shíjiān ma?</td><td>У тебя есть время?</td></tr>
</table>

<h3>2. Существование: «В/на месте есть X»</h3>
<p>Структура: <strong>地点 + 有 + 东西</strong></p>
<table>
  <tr><th>Китайский</th><th>Перевод</th></tr>
  <tr><td>桌子上<strong>有</strong>一杯水。</td><td>На столе есть стакан воды.</td></tr>
  <tr><td>学校里<strong>有</strong>很多学生。</td><td>В школе много студентов.</td></tr>
</table>

<h3>Отрицание: 没有 (méiyǒu)</h3>
<p>Отрицание 有 образуется с помощью <strong>没</strong>, а не 不:</p>
<ul>
  <li>我<strong>没有</strong>时间。— У меня нет времени.</li>
  <li>桌子上<strong>没有</strong>书。— На столе нет книги.</li>
</ul>
<p>⚠️ Нельзя сказать 不有 — только <strong>没有</strong>!</p>

<h3>Краткая форма</h3>
<p>В разговоре 没有 часто сокращают до 没：没时间 (нет времени).</p>""",
        "HSK-1",
        ["glagoly", "otritsanie"],
    ),
    (
        "Вопросительная частица 吗 (ma)",
        "chastitsa-ma",
        "Частица 吗 в конце предложения превращает утверждение в вопрос, требующий ответа «да» или «нет».",
        """<h2>Вопросительная частица 吗 (ma)</h2>
<p>Самый простой способ задать вопрос в китайском — добавить <strong>吗</strong> в конец утвердительного предложения. Никаких изменений порядка слов!</p>

<h3>Структура</h3>
<p><strong>Утверждение + 吗？</strong></p>

<h3>Примеры</h3>
<table>
  <tr><th>Утверждение</th><th>Вопрос с 吗</th><th>Перевод вопроса</th></tr>
  <tr><td>你好。(Привет.)</td><td>你好<strong>吗</strong>？</td><td>Как ты? / Ты хорошо?</td></tr>
  <tr><td>他是学生。(Он студент.)</td><td>他是学生<strong>吗</strong>？</td><td>Он студент?</td></tr>
  <tr><td>你吃饭。(Ты ешь.)</td><td>你吃饭<strong>吗</strong>？</td><td>Ты ешь?</td></tr>
  <tr><td>她喜欢中文。(Она любит китайский.)</td><td>她喜欢中文<strong>吗</strong>？</td><td>Она любит китайский?</td></tr>
</table>

<h3>Ответы</h3>
<ul>
  <li>Положительный: повторяем глагол или говорим <strong>是的 / 对</strong> (да, верно).</li>
  <li>Отрицательный: <strong>不</strong> + глагол, или <strong>不是</strong>.</li>
</ul>
<p>你是学生吗？— 是的，我是学生。/ 不，我不是学生，我是老师。</p>

<h3>Когда НЕ нужна 吗</h3>
<p>Если в вопросе уже есть вопросительное слово (什么、哪里、谁、几), 吗 не добавляется:</p>
<ul>
  <li>你去<strong>哪里</strong>？— Куда ты идёшь? (без 吗)</li>
  <li>这是<strong>什么</strong>？— Что это? (без 吗)</li>
</ul>""",
        "HSK-1",
        ["voprosy", "chastitsy"],
    ),
    (
        "Отрицание 不 (bù) — настоящее и будущее",
        "otritsanie-bu",
        "Частица 不 (bù) отрицает глаголы и прилагательные в настоящем и будущем времени.",
        """<h2>Отрицание 不 (bù)</h2>
<p><strong>不</strong> ставится <em>перед</em> глаголом или прилагательным для выражения отрицания в настоящем или будущем.</p>

<h3>Структура</h3>
<p><strong>S + 不 + V/Adj</strong></p>

<h3>Примеры с глаголами</h3>
<table>
  <tr><th>Утверждение</th><th>Отрицание</th><th>Перевод</th></tr>
  <tr><td>我吃饭。</td><td>我<strong>不</strong>吃饭。</td><td>Я не ем (сейчас / вообще).</td></tr>
  <tr><td>他去学校。</td><td>他<strong>不</strong>去学校。</td><td>Он не идёт в школу.</td></tr>
  <tr><td>我喜欢咖啡。</td><td>我<strong>不</strong>喜欢咖啡。</td><td>Мне не нравится кофе.</td></tr>
  <tr><td>她想去。</td><td>她<strong>不</strong>想去。</td><td>Она не хочет идти.</td></tr>
</table>

<h3>Примеры с прилагательными</h3>
<table>
  <tr><th>Утверждение</th><th>Отрицание</th><th>Перевод</th></tr>
  <tr><td>这件衣服贵。</td><td>这件衣服<strong>不</strong>贵。</td><td>Эта одежда не дорогая.</td></tr>
  <tr><td>今天热。</td><td>今天<strong>不</strong>热。</td><td>Сегодня не жарко.</td></tr>
</table>

<h3>Тон 不: изменение при следующем 4-м тоне</h3>
<p>不 читается bù (4-й тон), но перед словом с 4-м тоном меняется на <strong>bú</strong> (2-й тон):</p>
<ul>
  <li>不 + 是 (shì) → <strong>bú shì</strong> (不是)</li>
  <li>不 + 对 (duì) → <strong>bú duì</strong> (не правильно)</li>
</ul>

<h3>Исключение: 没有, а не 不有</h3>
<p>Глагол 有 отрицается через <strong>没有</strong>, а не 不有. Это единственное исключение для 不.</p>""",
        "HSK-1",
        ["otritsanie", "chastitsy"],
    ),
    (
        "Отрицание 没 (méi) — прошедшее и факты",
        "otritsanie-mei",
        "Частица 没 (méi) отрицает действия, которые не произошли, или факт обладания чем-либо.",
        """<h2>Отрицание 没 (méi)</h2>
<p><strong>没</strong> используется в двух случаях: отрицание <strong>прошедших действий</strong> и отрицание 有 (наличие/обладание).</p>

<h3>1. Отрицание прошедшего: «не сделал»</h3>
<p>Структура: <strong>S + 没(有) + V</strong></p>
<table>
  <tr><th>Китайский</th><th>Перевод</th></tr>
  <tr><td>我<strong>没</strong>吃饭。</td><td>Я не ел (не поел).</td></tr>
  <tr><td>他<strong>没</strong>去学校。</td><td>Он не ходил в школу.</td></tr>
  <tr><td>她<strong>没</strong>睡觉。</td><td>Она не спала.</td></tr>
  <tr><td>我<strong>没有</strong>看那部电影。</td><td>Я не смотрел этот фильм.</td></tr>
</table>

<h3>2. Отрицание 有: «нет в наличии»</h3>
<p>Структура: <strong>S + 没有 + N</strong></p>
<ul>
  <li>我<strong>没有</strong>钱。— У меня нет денег.</li>
  <li>这里<strong>没有</strong>厕所。— Здесь нет туалета.</li>
</ul>

<h3>不 vs 没: главное различие</h3>
<table>
  <tr><th></th><th>不 (bù)</th><th>没 (méi)</th></tr>
  <tr><td>Время</td><td>Настоящее / будущее</td><td>Прошедшее</td></tr>
  <tr><td>Значение</td><td>Намерение / привычка / факт</td><td>Действие не произошло</td></tr>
  <tr><td>Пример</td><td>我不吃肉。(Я не ем мясо — вообще)</td><td>我没吃肉。(Я не ел мясо — сегодня)</td></tr>
</table>

<h3>Диалог</h3>
<p><strong>A:</strong> 你吃早饭了吗？— Ты завтракал?<br>
<strong>B:</strong> 没有，我<strong>没</strong>吃。— Нет, не ел.<br>
<strong>A:</strong> 你不吃早饭吗？— Ты вообще не завтракаешь?<br>
<strong>B:</strong> 我一般不吃。— Обычно не ем.</p>""",
        "HSK-1",
        ["otritsanie", "chastitsy"],
    ),
    (
        "Частица 的 (de) — атрибутивная конструкция",
        "chastitsa-de",
        "Частица 的 связывает определение с определяемым словом, обозначая принадлежность и описание.",
        """<h2>Частица 的 (de) — атрибутивная конструкция</h2>
<p>Частица <strong>的</strong> ставится между определением и определяемым словом: «(чьё?) + 的 + (что?)».</p>

<h3>1. Принадлежность</h3>
<p>Структура: <strong>Владелец + 的 + Предмет</strong></p>
<table>
  <tr><th>Китайский</th><th>Перевод</th></tr>
  <tr><td>我<strong>的</strong>书</td><td>Моя книга</td></tr>
  <tr><td>老师<strong>的</strong>名字</td><td>Имя учителя</td></tr>
  <tr><td>中国<strong>的</strong>文化</td><td>Культура Китая</td></tr>
  <tr><td>我们<strong>的</strong>学校</td><td>Наша школа</td></tr>
</table>

<h3>2. Описание (прилагательное + 的 + существительное)</h3>
<table>
  <tr><th>Китайский</th><th>Перевод</th></tr>
  <tr><td>漂亮<strong>的</strong>女孩</td><td>Красивая девушка</td></tr>
  <tr><td>很好<strong>的</strong>朋友</td><td>Очень хороший друг</td></tr>
  <tr><td>新<strong>的</strong>手机</td><td>Новый телефон</td></tr>
</table>

<h3>Когда 的 можно опустить</h3>
<p>Между личными местоимениями и словами близкого родства 的 часто опускается:</p>
<ul>
  <li>我妈妈 (вместо 我的妈妈) — моя мама</li>
  <li>她爸爸 — её папа</li>
  <li>我们学校 — наша школа</li>
</ul>

<h3>的 в конце предложения — существительное implied</h3>
<p>Если предмет очевиден, можно сказать только «的»:</p>
<ul>
  <li>这是谁<strong>的</strong>？— Чьё это? (= чья это вещь?)</li>
  <li>这是我<strong>的</strong>。— Это моё.</li>
</ul>""",
        "HSK-1",
        ["chastitsy", "struktura-predlozheniya"],
    ),
    (
        "Местоимения: я, ты, он/она, мы, вы, они",
        "mestoimeniya",
        "Личные местоимения в китайском языке не изменяются по падежам — одна форма для всех ролей.",
        """<h2>Местоимения в китайском языке</h2>
<p>В китайском нет падежей. Местоимение всегда выглядит одинаково — независимо от того, является ли оно подлежащим, дополнением или определением.</p>

<h3>Единственное число</h3>
<table>
  <tr><th>Иероглиф</th><th>Пиньинь</th><th>Значение</th></tr>
  <tr><td><strong>我</strong></td><td>wǒ</td><td>я / меня / мне / мной</td></tr>
  <tr><td><strong>你</strong></td><td>nǐ</td><td>ты / тебя / тебе</td></tr>
  <tr><td><strong>您</strong></td><td>nín</td><td>Вы (вежливое)</td></tr>
  <tr><td><strong>他</strong></td><td>tā</td><td>он</td></tr>
  <tr><td><strong>她</strong></td><td>tā</td><td>она</td></tr>
  <tr><td><strong>它</strong></td><td>tā</td><td>оно (для неодушевлённых)</td></tr>
</table>

<h3>Множественное число: + 们 (men)</h3>
<table>
  <tr><th>Иероглиф</th><th>Пиньинь</th><th>Значение</th></tr>
  <tr><td><strong>我们</strong></td><td>wǒmen</td><td>мы</td></tr>
  <tr><td><strong>你们</strong></td><td>nǐmen</td><td>вы</td></tr>
  <tr><td><strong>他们 / 她们</strong></td><td>tāmen</td><td>они (м./ж.)</td></tr>
</table>

<h3>Притяжательные: местоимение + 的</h3>
<ul>
  <li>我<strong>的</strong> — мой, моя, моё, мои</li>
  <li>你<strong>的</strong> — твой</li>
  <li>他<strong>的</strong> — его</li>
  <li>我们<strong>的</strong> — наш</li>
</ul>

<h3>Примеры</h3>
<ul>
  <li><strong>我</strong>是学生，<strong>他</strong>是老师。— Я студент, он учитель.</li>
  <li>老师叫<strong>我们</strong>回家。— Учитель попросил нас идти домой.</li>
  <li>这是<strong>你的</strong>书吗？— Это твоя книга?</li>
</ul>""",
        "HSK-1",
        ["mestoimeniya", "struktura-predlozheniya"],
    ),
    (
        "Счётные слова (量词 liàngcí)",
        "schyotnyye-slova",
        "В китайском языке между числительным и существительным обязательно стоит счётное слово (классификатор).",
        """<h2>Счётные слова 量词 (liàngcí)</h2>
<p>В китайском нельзя поставить число прямо перед существительным. Нужен <strong>классификатор</strong>: <strong>Число + 量词 + Существительное</strong>.</p>
<p>Это как сказать «три штуки книг» или «два листа бумаги» — только это правило <em>обязательно</em> для всех существительных.</p>

<h3>Основные счётные слова</h3>
<table>
  <tr><th>量词</th><th>Пиньинь</th><th>Для чего</th><th>Пример</th></tr>
  <tr><td><strong>个</strong></td><td>gè</td><td>Люди, общие предметы</td><td>一个人 (один человек), 三个苹果 (три яблока)</td></tr>
  <tr><td><strong>本</strong></td><td>běn</td><td>Книги, тетради</td><td>一本书 (одна книга), 两本杂志</td></tr>
  <tr><td><strong>张</strong></td><td>zhāng</td><td>Плоские предметы (бумага, стол, лицо)</td><td>一张纸 (лист бумаги), 一张桌子</td></tr>
  <tr><td><strong>杯</strong></td><td>bēi</td><td>Напитки в стакане/чашке</td><td>一杯水 (стакан воды), 一杯咖啡</td></tr>
  <tr><td><strong>条</strong></td><td>tiáo</td><td>Длинные гибкие предметы (рыба, брюки, улица)</td><td>一条鱼 (одна рыба), 一条裤子</td></tr>
  <tr><td><strong>只</strong></td><td>zhī</td><td>Животные, некоторые предметы парами</td><td>一只猫 (кот), 一只手 (одна рука)</td></tr>
  <tr><td><strong>件</strong></td><td>jiàn</td><td>Одежда (верхняя), вещи</td><td>一件衣服 (одна одежда), 一件事 (одно дело)</td></tr>
</table>

<h3>Универсальный классификатор 个</h3>
<p>Если не знаете точный классификатор, <strong>个</strong> подойдёт в большинстве случаев для разговорной речи.</p>

<h3>Структура с числом</h3>
<p><strong>数字 + 量词 + 名词</strong></p>
<ul>
  <li>两<strong>本</strong>书 — две книги</li>
  <li>三<strong>杯</strong>茶 — три чашки чая</li>
  <li>五<strong>个</strong>学生 — пять студентов</li>
</ul>

<h3>Вопросительное 几 (сколько?)</h3>
<p>几 + 量词 + 名词: <strong>几本书</strong>？— Сколько книг?</p>""",
        "HSK-1",
        ["chisla-i-schyot", "struktura-predlozheniya"],
    ),
    (
        "Порядок слов с обстоятельством времени",
        "poryadok-slov-vremya",
        "В китайском языке обстоятельство времени стоит ПЕРЕД глаголом, а не после него как в русском.",
        """<h2>Порядок слов с обстоятельством времени</h2>
<p>В русском мы часто говорим «Я пойду <em>завтра</em>» — время в конце. В китайском время ставится <strong>ближе к началу</strong> предложения, <em>перед</em> глаголом.</p>

<h3>Схема</h3>
<p><strong>S + Время + V + O</strong></p>
<p>или</p>
<p><strong>Время + S + V + O</strong> (если время — тема)</p>

<h3>Примеры</h3>
<table>
  <tr><th>Китайский</th><th>Пиньинь</th><th>Перевод</th></tr>
  <tr><td>我<strong>明天</strong>去北京。</td><td>Wǒ míngtiān qù Běijīng.</td><td>Я завтра еду в Пекин.</td></tr>
  <tr><td>她<strong>每天</strong>学习中文。</td><td>Tā měitiān xuéxí Zhōngwén.</td><td>Она каждый день учит китайский.</td></tr>
  <tr><td><strong>现在</strong>我很忙。</td><td>Xiànzài wǒ hěn máng.</td><td>Сейчас я очень занят.</td></tr>
  <tr><td>我们<strong>下午两点</strong>见面。</td><td>Wǒmen xiàwǔ liǎngdiǎn jiànmiàn.</td><td>Мы встретимся в 14:00.</td></tr>
</table>

<h3>Слова времени</h3>
<table>
  <tr><th>Слово</th><th>Пиньинь</th><th>Значение</th></tr>
  <tr><td>现在</td><td>xiànzài</td><td>сейчас</td></tr>
  <tr><td>今天</td><td>jīntiān</td><td>сегодня</td></tr>
  <tr><td>明天</td><td>míngtiān</td><td>завтра</td></tr>
  <tr><td>昨天</td><td>zuótiān</td><td>вчера</td></tr>
  <tr><td>每天</td><td>měitiān</td><td>каждый день</td></tr>
  <tr><td>以前</td><td>yǐqián</td><td>раньше, прежде</td></tr>
  <tr><td>以后</td><td>yǐhòu</td><td>потом, впоследствии</td></tr>
</table>

<h3>Неверно / Верно</h3>
<ul>
  <li>❌ 我去北京明天。(Время в конце — ошибка)</li>
  <li>✅ 我<strong>明天</strong>去北京。</li>
</ul>""",
        "HSK-1",
        ["vremya", "struktura-predlozheniya"],
    ),
    (
        "Аспектная частица 了 (le) — завершённое действие",
        "chastitsa-le",
        "Частица 了 после глагола показывает, что действие завершилось или произошло изменение ситуации.",
        """<h2>Аспектная частица 了 (le)</h2>
<p>了 — одна из самых важных и сложных частиц китайского. Она не обозначает прошедшее время само по себе, а указывает на <strong>завершённость</strong> действия или <strong>изменение ситуации</strong>.</p>

<h3>1. 了 после глагола — действие выполнено</h3>
<p>Структура: <strong>S + V + 了 + O</strong></p>
<table>
  <tr><th>Китайский</th><th>Пиньинь</th><th>Перевод</th></tr>
  <tr><td>我吃<strong>了</strong>饭。</td><td>Wǒ chī le fàn.</td><td>Я поел.</td></tr>
  <tr><td>她买<strong>了</strong>一本书。</td><td>Tā mǎi le yī běn shū.</td><td>Она купила книгу.</td></tr>
  <tr><td>他去<strong>了</strong>北京。</td><td>Tā qù le Běijīng.</td><td>Он съездил в Пекин.</td></tr>
</table>

<h3>2. 了 в конце предложения — изменение ситуации</h3>
<p>Структура: <strong>Предложение + 了</strong> (показывает новое состояние)</p>
<ul>
  <li>我累<strong>了</strong>。— Я устал (стал устать).</li>
  <li>他是老师<strong>了</strong>。— Он теперь учитель (стал учителем).</li>
  <li>春天来<strong>了</strong>！— Пришла весна!</li>
</ul>

<h3>Отрицание с 了: используем 没(有)</h3>
<p>Чтобы отрицать завершённое действие — убираем 了 и добавляем 没：</p>
<ul>
  <li>我<strong>没</strong>吃饭。— Я не ел. (без 了)</li>
  <li>她<strong>没有</strong>买书。— Она не покупала книгу.</li>
</ul>

<h3>Вопрос с 了</h3>
<p>Добавляем 吗 или используем форму V了没有？:</p>
<ul>
  <li>你吃了吗？— Ты поел?</li>
  <li>你吃了没有？— Ты поел или нет?</li>
</ul>

<h3>Важно</h3>
<p>了 ≠ прошедшее время. Глагол без 了 тоже может быть в прошлом: 昨天我去学校 (Вчера я ходил в школу) — 了 необязательно при наличии слова времени.</p>""",
        "HSK-1",
        ["chastitsy", "glagoly"],
    ),
    (
        "Вопросительные слова: 什么、哪里、谁、几、怎么",
        "voprositelnyye-slova",
        "Китайский язык использует вопросительные слова на том же месте, где стоял бы ответ — без изменения порядка слов.",
        """<h2>Вопросительные слова</h2>
<p>В отличие от русского, в китайском <strong>не нужно переставлять слова</strong> для вопроса. Вопросительное слово занимает место того слова, о котором мы спрашиваем.</p>

<h3>Основные вопросительные слова</h3>
<table>
  <tr><th>Слово</th><th>Пиньинь</th><th>Значение</th><th>Пример</th></tr>
  <tr><td><strong>什么</strong></td><td>shénme</td><td>что? какой?</td><td>这是<strong>什么</strong>？— Что это?</td></tr>
  <tr><td><strong>谁</strong></td><td>shéi / shuí</td><td>кто?</td><td><strong>谁</strong>是你的老师？— Кто твой учитель?</td></tr>
  <tr><td><strong>哪里/哪儿</strong></td><td>nǎlǐ / nǎr</td><td>где? куда?</td><td>你去<strong>哪里</strong>？— Куда ты идёшь?</td></tr>
  <tr><td><strong>什么时候</strong></td><td>shénme shíhou</td><td>когда?</td><td>你<strong>什么时候</strong>来？— Когда ты придёшь?</td></tr>
  <tr><td><strong>为什么</strong></td><td>wèishénme</td><td>почему?</td><td>你<strong>为什么</strong>学中文？— Почему ты учишь китайский?</td></tr>
  <tr><td><strong>怎么</strong></td><td>zěnme</td><td>как? каким образом?</td><td>你<strong>怎么</strong>来的？— Как ты добрался?</td></tr>
  <tr><td><strong>几</strong></td><td>jǐ</td><td>сколько? (до 10)</td><td>你有<strong>几</strong>本书？— Сколько у тебя книг?</td></tr>
  <tr><td><strong>多少</strong></td><td>duōshao</td><td>сколько? (любое количество)</td><td>这个<strong>多少</strong>钱？— Сколько это стоит?</td></tr>
</table>

<h3>Принцип «на своём месте»</h3>
<p>Сравним: «Ты идёшь КУДА?» → вопросительное слово на месте ответа</p>
<ul>
  <li>你去<strong>北京</strong>。(Ты идёшь в Пекин.) → 你去<strong>哪里</strong>？(Ты идёшь куда?)</li>
  <li>她是<strong>老师</strong>。(Она учитель.) → 她是<strong>什么</strong>？(Она кто?)</li>
</ul>

<h3>Важно: без 吗</h3>
<p>С вопросительными словами (что, кто, где...) частицу 吗 не добавляют!</p>
<ul>
  <li>✅ 你去哪里？</li>
  <li>❌ 你去哪里吗？(ошибка)</li>
</ul>""",
        "HSK-1",
        ["voprosy", "struktura-predlozheniya"],
    ),
    (
        "Степень прилагательных: 很、非常、有点、太",
        "stepen-prilagatelnyh",
        "Интенсивность прилагательного в китайском языке выражается наречиями меры: 很 (очень), 非常 (крайне), 有点 (немного), 太 (слишком).",
        """<h2>Степень прилагательных: наречия меры</h2>
<p>В китайском языке прилагательное-сказуемое почти всегда сопровождается <strong>наречием меры</strong>. Голое прилагательное звучит как сравнение.</p>

<h3>Основные наречия</h3>
<table>
  <tr><th>Слово</th><th>Пиньинь</th><th>Значение</th><th>Пример</th></tr>
  <tr><td><strong>很</strong></td><td>hěn</td><td>очень (нейтральное)</td><td>今天<strong>很</strong>热。— Сегодня жарко.</td></tr>
  <tr><td><strong>非常</strong></td><td>fēicháng</td><td>очень, крайне</td><td>这个电影<strong>非常</strong>好看。— Этот фильм очень хорош.</td></tr>
  <tr><td><strong>有点</strong></td><td>yǒudiǎn</td><td>немного, чуть-чуть</td><td>我<strong>有点</strong>累。— Я немного устал.</td></tr>
  <tr><td><strong>太…了</strong></td><td>tài…le</td><td>слишком; восклицательно</td><td>这<strong>太</strong>贵<strong>了</strong>！— Это слишком дорого!</td></tr>
  <tr><td><strong>真</strong></td><td>zhēn</td><td>действительно, правда</td><td><strong>真</strong>好吃！— Правда вкусно!</td></tr>
</table>

<h3>Почему 很 — не просто «очень»</h3>
<p>В предложении 她漂亮 (без наречия) звучит как «она красивее (чем кто-то)». Поэтому обычно говорят 她<strong>很</strong>漂亮 — просто «она красивая», без интенсивного значения «очень».</p>

<h3>有点 — только для негативного или нейтрального</h3>
<p>有点 чаще с прилагательными с негативным оттенком или нейтральными:</p>
<ul>
  <li>✅ 我有点累。/ 有点贵。/ 有点冷。</li>
  <li>Сомнительно: 有点高兴 (немного рад — звучит неестественно)</li>
</ul>

<h3>太…了 — восклицание или жалоба</h3>
<ul>
  <li>太好了！— Отлично! (восторг)</li>
  <li>太难了！— Слишком сложно! (жалоба)</li>
  <li>太贵了！— Слишком дорого!</li>
</ul>""",
        "HSK-1",
        ["prilagatelnyye", "struktura-predlozheniya"],
    ),
]


def seed():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Теги ──────────────────────────────────────────────────
    tag_id_map = {}
    for name, slug in TAGS:
        cur.execute("SELECT id FROM grammar_tags WHERE slug = %s", (slug,))
        row = cur.fetchone()
        if row:
            tag_id_map[slug] = row[0]
            print(f"[SKIP] Тег уже существует: {name}")
        else:
            cur.execute(
                "INSERT INTO grammar_tags (name, slug) VALUES (%s, %s) RETURNING id",
                (name, slug),
            )
            tag_id_map[slug] = cur.fetchone()[0]
            print(f"[ADD]  Тег: {name}")

    # ── Правила ───────────────────────────────────────────────
    for title, slug, description, content, hsk_level, tag_slugs in RULES:
        cur.execute("SELECT id FROM grammar_rules WHERE slug = %s", (slug,))
        row = cur.fetchone()
        if row:
            print(f"[SKIP] Правило уже существует: {title}")
            continue

        cur.execute(
            """INSERT INTO grammar_rules (title, slug, description, content, hsk_level)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (title, slug, description, content, hsk_level),
        )
        rule_id = cur.fetchone()[0]
        print(f"[ADD]  Правило: {title}")

        for tag_slug in tag_slugs:
            tag_id = tag_id_map.get(tag_slug)
            if tag_id:
                cur.execute(
                    "INSERT INTO grammar_rule_tags (rule_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (rule_id, tag_id),
                )

    conn.commit()
    cur.close()
    conn.close()
    print("\nГотово! Правила грамматики успешно добавлены.")


if __name__ == "__main__":
    seed()
