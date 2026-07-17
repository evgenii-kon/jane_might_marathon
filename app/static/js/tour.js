(function () {
  var IS_MOBILE = window.matchMedia('(max-width: 640px)').matches;

  var STEPS = [
    {
      title: 'Добро пожаловать В School Might!',
      description:
        'Это платформа для изучения китайского языка по программе HSK-1. Предлагаем прямо сейчас пройти короткую экскурсию — она займёт меньше минуты и покажет все основные разделы. Мы объясним тебе, как пользоваться платформой, как выстроить свое обучение, чтобы оно было и понятным и эффективным.<br><br>' +
        'Если хотите вернуться к ней позже, её всегда можно запустить снова в разделе «Профиль».',
    },
    {
      element: '#tour-profile',
      side: 'bottom',
      align: 'end',
      title: 'Ваш профиль',
      description:
        'Здесь хранится статистика и прогресс. Можно редактировать данные о себе, а также тут мы можете обучающий тур по платформе.',
    },
    {
      element: '#tour-articles',
      side: 'bottom',
      align: 'start',
      title: 'Статьи',
      description:
        'Здесь собраны полезные материалы о китайском языке и культуре — чтение таких статей помогает лучше понимать восточную культуру.<br><br>' +
        'Читайте эти статьи время от времени — это будет прекрасным дополнением к обучению после изучения теории и грамматики.',
    },
    {
      element: '#tour-idioms',
      side: 'bottom',
      align: 'start',
      title: 'Идиомы',
      description:
        'Чэнъюй — четырёхсловные идиомы с богатой историей. Знание таких речевых структур серьезно повышает твой навык обращения с языком. Используя их ты дашь собеседнику понять, что ты говоришь как настоящие носители языка.<br><br>' +
        'В этот разделе реализован самоконтроль в изучении материала. Переводите идиомы из раздела «Не знаю», в размер «Знаю хорошо», чтобы не путать уже изученный материал, и тот что еще предстоит пройти.',
    },
    {
      element: '#tour-grammar',
      side: 'bottom',
      align: 'start',
      title: 'Грамматика',
      description:
        'Здесь хранятся правила и конструкции HSK-1 с примерами и таблицами.<br><br>' +
        'Проходить грамматику ты будешь и на уроках, однако чтобы при желании повторить определенное правило не нужно было искать в текстовых или видео уроках информацию, мы подготовили раздел где коротко описаны все грамматические конструкции с примерами.<br><br>' +
        'А быстро найти нужное правило ты можешь применив фильтрацию по тегам.<br><br>' +
        'Заходи в этот блок для того чтобы закреплять грамматику, уже пройденную на уроках.',
    },
    {
      element: '#tour-reading',
      side: 'bottom',
      align: 'start',
      title: 'Тексты для чтения',
      description:
        'Короткие тексты на китайском языке с пиньинем и переводом, а после каждого — тест на понимание прочитанного.<br><br>' +
        'Это отличный способ закрепить лексику из уроков в живом контексте. Читай тексты по мере прохождения курса — они подобраны специально из слов HSK-1.',
    },
    {
      element: '#tour-trainer',
      side: 'bottom',
      align: 'start',
      title: 'Тренажёр слов',
      description:
        'В этом разделе собраны тренажеры по словам.<br><br>' +
        'В настоящий момент тут есть 2 режима: режим повторения всех слов уровня HSK-1, а также режим ежедневного повторения.<br><br>' +
        'Рекомендуем пользоваться режимом ежедневного повторения регулярно. Тут тебя будут встречать только те слова, которые ты уже прошел на уроках, а также они отбираются ежедневно по системе кривой Эббингауза — система сама понимает, какие слова даются тебе хорошо, а какие необходимо повторить. Это крайне мощная стратегия для запоминания слов!',
    },
    {
      element: '#tour-rating',
      side: 'left',
      align: 'start',
      title: 'Рейтинг слов',
      description:
        'В этой вкладке хранится все история твоих ответов в тренажерах. Здесь можно оценить прогресс самостоятельно. Для каждого слова существует Mastery level, который или растет или снижается после правильных/неправильных ответов.<br><br>' +
        'Постирайте достичь максимального уровня по каждому слову!',
    },
    {
      element: '.activity-section',
      side: 'right',
      align: 'start',
      title: 'Активность',
      description:
        'Календарь фиксирует дни занятий и помогает держать streak. Чем больше активности вы проявляете за день — тем более насыщенная становится отметка для в календаре.<br>' +
        'Занимайтесь каждый день, чтобы серия не прерывалась!',
    },
    {
      element: '#tour-weeks',
      side: 'top',
      align: 'start',
      title: 'Недели марафона',
      description:
        'Это основная вкладка, с которой тебе предстоит работать.<br>' +
        'Курс разбит на 6 недель. Каждая открывается последовательно и содержит уроки, слова и упражнения.<br>' +
        'Заходи сюда ежедневно и изучай уроки.',
    },
    {
      title: 'Так выглядят уроки внутри недели',
      description:
        'Каждый урок — это отдельная карточка. Нажми «Начать», чтобы открыть материал.' +
        '<div class="week-lesson-row hsk-mock-row">' +
          '<div class="wl-info">' +
            '<div class="wl-number">6</div>' +
            '<div class="wl-details">' +
              '<div class="wl-name">Историческая лексика</div>' +
              '<div class="wl-desc">Изучите новую тему</div>' +
              '<div class="wl-exercises-badge"><span>📝 Упражнения: 0/4</span></div>' +
            '</div>' +
          '</div>' +
          '<div class="wl-actions">' +
            '<span class="wl-btn wl-btn-start">🚀 Начать</span>' +
          '</div>' +
        '</div>',
    },
    {
      title: 'После теории появляются упражнения',
      description:
        'Как только ты изучишь теорию урока, появится кнопка «Упражнения» — обязательно выполни их для закрепления материала.' +
        '<div class="week-lesson-row wl-completed hsk-mock-row">' +
          '<div class="wl-info">' +
            '<div class="wl-number">6</div>' +
            '<div class="wl-details">' +
              '<div class="wl-name">Историческая лексика</div>' +
              '<div class="wl-desc">Изучите новую тему</div>' +
              '<div class="wl-exercises-badge"><span>📝 Упражнения: 0/4</span></div>' +
            '</div>' +
          '</div>' +
          '<div class="wl-actions">' +
            '<span class="wl-btn wl-btn-exercises">✍️ Упражнения</span>' +
            '<span class="wl-btn wl-btn-done">✅ Теория</span>' +
          '</div>' +
        '</div>',
    },
    {
      title: 'Урок завершён!',
      description:
        'Когда теория изучена и все упражнения выполнены — появляется метка «Все выполнены». Так ты отслеживаешь, что уже пройдено.' +
        '<div class="week-lesson-row wl-completed hsk-mock-row">' +
          '<div class="wl-info">' +
            '<div class="wl-number">6</div>' +
            '<div class="wl-details">' +
              '<div class="wl-name">Историческая лексика</div>' +
              '<div class="wl-desc">Изучите новую тему</div>' +
              '<div class="wl-exercises-badge"><span>📝 Упражнения: 4/4</span> <span class="wl-exercises-done">✅ Все выполнены</span></div>' +
            '</div>' +
          '</div>' +
          '<div class="wl-actions">' +
            '<span class="wl-btn wl-btn-exercises-done">✅ Упражнения</span>' +
            '<span class="wl-btn wl-btn-done">✅ Теория</span>' +
          '</div>' +
        '</div>',
    },
    {
      title: '🚀 Готовы начать?',
      description: 'Открой первую неделю и сделайте первый шаг навстречу китайскому языку!',
    },
  ];

  if (localStorage.getItem('tour_completed')) return;

  if (IS_MOBILE) {
    initMobileSlideshow();
  } else {
    initDesktopTour();
  }

  // ---------- Mobile: full-screen slideshow, no page anchoring ----------
  function initMobileSlideshow() {
    var style = document.createElement('style');
    style.textContent = `
      .hsk-slide-overlay {
        position: fixed;
        inset: 0;
        background: rgba(17, 8, 6, 0.68);
        z-index: 1000000000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 16px;
      }
      .hsk-slide-card {
        position: relative;
        background: var(--surface);
        border: 2px solid var(--blue);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        width: 100%;
        max-width: 420px;
        max-height: 82vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      .hsk-slide-skip {
        position: absolute;
        top: 10px;
        right: 12px;
        border: none;
        background: transparent;
        color: var(--gray);
        font-size: 22px;
        line-height: 1;
        padding: 6px;
        cursor: pointer;
        z-index: 1;
      }
      .hsk-slide-skip:hover { color: var(--red); }
      .hsk-slide-body {
        padding: 28px 22px 16px;
        overflow-y: auto;
      }
      .hsk-slide-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: var(--black);
        margin: 0;
        line-height: 1.3;
      }
      .hsk-slide-desc {
        font-family: 'Montserrat', sans-serif;
        font-size: 13.5px;
        line-height: 1.55;
        color: var(--gray);
        margin-top: 10px;
      }
      .hsk-slide-desc .hsk-mock-row {
        margin-top: 14px;
        padding: 10px 12px;
        gap: 10px;
        flex-wrap: wrap;
      }
      .hsk-slide-footer {
        padding: 14px 22px 18px;
        border-top: 2px solid var(--blue);
      }
      .hsk-progress-track {
        height: 8px;
        background: rgba(149, 187, 234, 0.3);
        border-radius: 999px;
        overflow: hidden;
      }
      .hsk-progress-fill {
        height: 100%;
        background: var(--red);
        border-radius: 999px;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .hsk-progress-label {
        display: block;
        margin-top: 6px;
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 600;
        color: var(--gray);
        text-align: right;
      }
      .hsk-slide-btns {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
      .hsk-slide-btns button {
        flex: 1;
        border-radius: 50px;
        padding: 12px 16px;
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.2s, opacity 0.2s;
      }
      .hsk-slide-next {
        background: var(--red);
        color: var(--white);
        border: none;
        flex-grow: 2;
      }
      .hsk-slide-next:hover {
        transform: translateY(-2px);
        opacity: 0.9;
      }
      .hsk-slide-prev {
        background: var(--surface);
        color: var(--red);
        border: 2px solid var(--red);
      }
      .hsk-slide-prev:disabled {
        opacity: 0.25;
        cursor: default;
      }
      @media (max-width: 380px) {
        .hsk-slide-desc .wl-number { display: none; }
      }
    `;
    document.head.appendChild(style);

    var overlay = document.createElement('div');
    overlay.className = 'hsk-slide-overlay';
    overlay.innerHTML =
      '<div class="hsk-slide-card">' +
        '<button type="button" class="hsk-slide-skip" aria-label="Закрыть">×</button>' +
        '<div class="hsk-slide-body">' +
          '<h3 class="hsk-slide-title"></h3>' +
          '<div class="hsk-slide-desc"></div>' +
        '</div>' +
        '<div class="hsk-slide-footer">' +
          '<div class="hsk-progress-track"><div class="hsk-progress-fill"></div></div>' +
          '<span class="hsk-progress-label"></span>' +
          '<div class="hsk-slide-btns">' +
            '<button type="button" class="hsk-slide-prev">← Назад</button>' +
            '<button type="button" class="hsk-slide-next">Далее →</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var titleEl = overlay.querySelector('.hsk-slide-title');
    var descEl = overlay.querySelector('.hsk-slide-desc');
    var fillEl = overlay.querySelector('.hsk-progress-fill');
    var labelEl = overlay.querySelector('.hsk-progress-label');
    var bodyEl = overlay.querySelector('.hsk-slide-body');
    var prevBtn = overlay.querySelector('.hsk-slide-prev');
    var nextBtn = overlay.querySelector('.hsk-slide-next');
    var skipBtn = overlay.querySelector('.hsk-slide-skip');

    var idx = 0;

    function render() {
      var step = STEPS[idx];
      titleEl.textContent = step.title;
      descEl.innerHTML = step.description;
      bodyEl.scrollTop = 0;
      fillEl.style.width = Math.round(((idx + 1) / STEPS.length) * 100) + '%';
      labelEl.textContent = (idx + 1) + ' / ' + STEPS.length;
      prevBtn.disabled = idx === 0;
      nextBtn.textContent = idx === STEPS.length - 1 ? 'Начать учиться!' : 'Далее →';
    }

    function finish() {
      localStorage.setItem('tour_completed', 'true');
      document.body.style.overflow = '';
      overlay.remove();
    }

    prevBtn.addEventListener('click', function () {
      if (idx > 0) { idx--; render(); }
    });
    nextBtn.addEventListener('click', function () {
      if (idx < STEPS.length - 1) { idx++; render(); } else { finish(); }
    });
    skipBtn.addEventListener('click', finish);

    setTimeout(function () {
      document.body.style.overflow = 'hidden';
      document.body.appendChild(overlay);
      render();
    }, 800);
  }

  // ---------- Desktop: driver.js tour anchored to page elements ----------
  function initDesktopTour() {
    var style = document.createElement('style');
    style.textContent = `
      .driver-popover.hsk-tour-popover {
        background: var(--surface);
        border: 2px solid var(--blue);
        border-radius: 24px;
        box-shadow:
          0 8px 32px rgba(0, 0, 0, 0.14),
          0 1px 4px rgba(0, 0, 0, 0.06);
        padding: 42px 45px 33px;
        max-width: 570px;
        min-width: 450px;
      }
      .driver-popover.hsk-tour-popover .driver-popover-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 19px;
        font-weight: 700;
        color: var(--black);
        margin: 0;
        padding: 0;
        line-height: 1.3;
      }
      .driver-popover.hsk-tour-popover .driver-popover-description {
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        line-height: 1.65;
        color: var(--gray);
        margin: 10px 0 0;
        padding: 0;
      }
      .driver-popover.hsk-tour-popover .driver-popover-description .hsk-mock-row {
        margin-top: 14px;
      }
      .driver-popover.hsk-tour-popover .driver-popover-next-btn {
        background: var(--red);
        color: var(--white);
        padding: 14px 36px;
        border-radius: 50px;
        font-size: 15px;
        font-weight: 700;
        border: none;
        box-shadow: none;
        transition: transform 0.2s, opacity 0.2s;
        white-space: nowrap;
        cursor: pointer;
        text-shadow: none;
        -webkit-font-smoothing: antialiased;
      }
      .driver-popover.hsk-tour-popover .driver-popover-next-btn:hover {
        transform: translateY(-2px);
        opacity: 0.9;
      }
      .driver-popover.hsk-tour-popover .driver-popover-prev-btn {
        background: var(--surface);
        color: var(--red);
        padding: 14px 28px;
        border-radius: 50px;
        font-size: 15px;
        font-weight: 600;
        border: 2px solid var(--red);
        transition: background 0.2s, color 0.2s;
        white-space: nowrap;
        cursor: pointer;
      }
      .driver-popover.hsk-tour-popover .driver-popover-prev-btn:hover:not(:disabled) {
        background: var(--red);
        color: var(--white);
      }
      .driver-popover.hsk-tour-popover .driver-popover-prev-btn:disabled {
        opacity: 0.25;
        cursor: default;
      }
      .driver-popover.hsk-tour-popover .driver-popover-progress-text {
        flex: 1;
        display: flex;
        align-items: center;
      }
      .hsk-progress-track {
        flex: 1;
        height: 10px;
        background: rgba(149, 187, 234, 0.3);
        border-radius: 999px;
        overflow: hidden;
      }
      .hsk-progress-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 12px;
        font-weight: 600;
        color: var(--gray);
        white-space: nowrap;
        flex-shrink: 0;
      }
      .hsk-progress-fill {
        height: 100%;
        background: var(--red);
        border-radius: 999px;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      /* driver.js's popover arrow is hardcoded white in its base CSS; it only
         matched the old plain-white popover by coincidence. Re-point it at
         --surface so it still blends once the popover itself is themed. */
      .driver-popover-arrow {
        border-color: var(--surface);
      }
      .driver-popover.hsk-tour-popover .driver-popover-close-btn {
        color: var(--gray);
      }
      .driver-popover.hsk-tour-popover .driver-popover-close-btn:hover {
        color: var(--red);
      }
    `;
    document.head.appendChild(style);

    var { driver } = window.driver.js;

    function stopScroll(e) { e.preventDefault(); }
    function lockScroll()   {
      document.addEventListener('wheel',     stopScroll, { passive: false });
      document.addEventListener('touchmove', stopScroll, { passive: false });
    }
    function unlockScroll() {
      document.removeEventListener('wheel',     stopScroll);
      document.removeEventListener('touchmove', stopScroll);
    }

    // Шаги профиля/статей/идиом/грамматики/чтения указывают на пункты,
    // которые видимы только внутри открытого выпадающего меню в шапке.
    function openDropdownFor(selector) {
      document.querySelectorAll('.dropdown.force-open').forEach(function (el) {
        el.classList.remove('force-open');
      });
      var target = document.querySelector(selector);
      var dropdown = target && target.closest('.dropdown');
      if (dropdown) dropdown.classList.add('force-open');
    }

    function closeAllDropdowns() {
      document.querySelectorAll('.dropdown.force-open').forEach(function (el) {
        el.classList.remove('force-open');
      });
    }

    function renderProgressBar() {
      var footer = document.querySelector('.driver-popover.hsk-tour-popover .driver-popover-footer');
      var progressText = document.querySelector('.driver-popover.hsk-tour-popover .driver-popover-progress-text');
      if (!footer || !progressText) return;
      var idx = tour.getActiveIndex();
      var pct = Math.round(((idx + 1) / STEPS.length) * 100);

      // bar inside progress-text
      if (!progressText.querySelector('.hsk-progress-track')) {
        progressText.innerHTML = '<div class="hsk-progress-track"><div class="hsk-progress-fill"></div></div>';
      }
      var fill = progressText.querySelector('.hsk-progress-fill');
      if (fill) fill.style.width = pct + '%';

      // counter injected right before the prev button, inside its actual parent
      var label = footer.querySelector('.hsk-progress-label');
      if (!label) {
        label = document.createElement('span');
        label.className = 'hsk-progress-label';
        var prevBtn = footer.querySelector('.driver-popover-prev-btn');
        if (prevBtn && prevBtn.parentNode) {
          prevBtn.parentNode.insertBefore(label, prevBtn);
        }
      }
      label.textContent = (idx + 1) + ' / ' + STEPS.length;
    }

    var tour = driver({
      showProgress: true,
      progressText: ' ',
      nextBtnText: 'Далее →',
      prevBtnText: '← Назад',
      doneBtnText: 'Начать учиться!',
      popoverClass: 'hsk-tour-popover',
      stagePadding: 8,
      stageRadius: 14,
      onHighlightStarted: function () {
        var step = STEPS[tour.getActiveIndex()];
        var target = step && step.element ? document.querySelector(step.element) : null;
        if (target && target.closest('.dropdown-menu')) {
          openDropdownFor(step.element);
        } else {
          closeAllDropdowns();
        }

        // Weeks step: position top of section at ~45% of viewport height
        // so the popover fits above and header+cards are visible below
        if (tour.getActiveIndex() === 9) {
          var el = document.getElementById('tour-weeks');
          if (el) {
            var targetTop = el.getBoundingClientRect().top + window.scrollY - window.innerHeight * 0.42;
            window.scrollTo({ top: targetTop, behavior: 'instant' });
          }
        }
      },
      onHighlighted: function () {
        renderProgressBar();
      },
      onDestroyStarted: function () {
        unlockScroll();
        closeAllDropdowns();
        localStorage.setItem('tour_completed', 'true');
        tour.destroy();
      },
      steps: STEPS.map(function (step) {
        var entry = {
          popover: {
            title: step.title,
            description: step.description,
          },
        };
        if (step.element) {
          entry.element = step.element;
          entry.popover.side = step.side;
          entry.popover.align = step.align;
        }
        return entry;
      }),
    });

    setTimeout(function () {
      lockScroll();
      tour.drive();
    }, 800);
  }
})();
