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
        '<div class="hsk-mock-card" style="margin-top:14px;background:#f0f4ff;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #dce6ff;">' +
          '<div class="hsk-mock-badge" style="width:36px;height:36px;border-radius:50%;background:#6b7cff;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
          '<div style="flex:1;min-width:0;">' +
            '<div style="font-weight:700;font-size:14px;color:#1a1a2e;">Историческая лексика</div>' +
            '<div style="font-size:12px;color:#6b7cff;margin-top:2px;">Изучите новую тему</div>' +
            '<div style="font-size:11px;color:#888;margin-top:4px;">📝 Упражнения: 0/4</div>' +
          '</div>' +
          '<div style="background:linear-gradient(135deg,#2563eb,#60a5fa);color:#fff;border-radius:50px;padding:8px 18px;font-size:13px;font-weight:700;white-space:nowrap;">🚀 Начать</div>' +
        '</div>',
    },
    {
      title: 'После теории появляются упражнения',
      description:
        'Как только ты изучишь теорию урока, появится кнопка «Упражнения» — обязательно выполни их для закрепления материала.' +
        '<div class="hsk-mock-card" style="margin-top:14px;background:#f0f4ff;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #dce6ff;">' +
          '<div class="hsk-mock-badge" style="width:36px;height:36px;border-radius:50%;background:#22c55e;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
          '<div style="flex:1;min-width:0;">' +
            '<div style="font-weight:700;font-size:14px;color:#1a1a2e;">Историческая лексика</div>' +
            '<div style="font-size:12px;color:#6b7cff;margin-top:2px;">Изучите новую тему</div>' +
            '<div style="font-size:11px;color:#888;margin-top:4px;">📝 Упражнения: 0/4</div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;">' +
            '<div style="background:linear-gradient(135deg,#2563eb,#60a5fa);color:#fff;border-radius:50px;padding:8px 16px;font-size:13px;font-weight:700;white-space:nowrap;">✍️ Упражнения</div>' +
            '<div style="background:#dcfce7;color:#16a34a;border-radius:50px;padding:8px 14px;font-size:13px;font-weight:600;white-space:nowrap;border:1px solid #bbf7d0;">✅ Теория</div>' +
          '</div>' +
        '</div>',
    },
    {
      title: 'Урок завершён!',
      description:
        'Когда теория изучена и все упражнения выполнены — обе кнопки становятся зелёными и появляется метка «Все выполнены». Так ты отслеживаешь, что уже пройдено.' +
        '<div class="hsk-mock-card" style="margin-top:14px;background:#f0fff4;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #bbf7d0;">' +
          '<div class="hsk-mock-badge" style="width:36px;height:36px;border-radius:50%;background:#22c55e;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
          '<div style="flex:1;min-width:0;">' +
            '<div style="font-weight:700;font-size:14px;color:#1a1a2e;">Историческая лексика</div>' +
            '<div style="font-size:12px;color:#6b7cff;margin-top:2px;">Изучите новую тему</div>' +
            '<div style="font-size:11px;color:#888;margin-top:4px;display:flex;align-items:center;gap:8px;">📝 Упражнения: 4/4 <span style="background:#dcfce7;color:#16a34a;border-radius:20px;padding:2px 8px;font-size:10px;font-weight:600;border:1px solid #bbf7d0;">✅ Все выполнены</span></div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;">' +
            '<div style="background:#dcfce7;color:#16a34a;border-radius:50px;padding:8px 16px;font-size:13px;font-weight:600;white-space:nowrap;border:1px solid #bbf7d0;">✅ Упражнения</div>' +
            '<div style="background:#dcfce7;color:#16a34a;border-radius:50px;padding:8px 14px;font-size:13px;font-weight:600;white-space:nowrap;border:1px solid #bbf7d0;">✅ Теория</div>' +
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
        background: rgba(4, 13, 30, 0.72);
        z-index: 1000000000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 16px;
      }
      .hsk-slide-card {
        position: relative;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
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
        color: #b0b4bd;
        font-size: 22px;
        line-height: 1;
        padding: 6px;
        cursor: pointer;
        z-index: 1;
      }
      .hsk-slide-skip:hover { color: #4b5563; }
      .hsk-slide-body {
        padding: 28px 22px 16px;
        overflow-y: auto;
      }
      .hsk-slide-title {
        font-family: 'Onest', 'Inter', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #111827;
        margin: 0;
        line-height: 1.3;
      }
      .hsk-slide-desc {
        font-family: 'Inter', sans-serif;
        font-size: 13.5px;
        line-height: 1.55;
        color: #4b5563;
        margin-top: 10px;
      }
      .hsk-slide-desc .hsk-mock-card {
        padding: 10px 12px !important;
        gap: 10px !important;
        flex-wrap: wrap;
      }
      .hsk-slide-footer {
        padding: 14px 22px 18px;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
      }
      .hsk-progress-track {
        height: 8px;
        background: #e5e7eb;
        border-radius: 999px;
        overflow: hidden;
      }
      .hsk-progress-fill {
        height: 100%;
        background: #6366f1;
        border-radius: 999px;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .hsk-progress-label {
        display: block;
        margin-top: 6px;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 600;
        color: #9ca3af;
        text-align: right;
      }
      .hsk-slide-btns {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
      .hsk-slide-btns button {
        flex: 1;
        border: none;
        border-radius: 50px;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
      }
      .hsk-slide-next {
        background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
        color: #fff;
        box-shadow: 0 4px 20px rgba(96, 165, 250, 0.45);
        flex-grow: 2;
      }
      .hsk-slide-prev {
        background: transparent;
        color: #2563eb;
        border: 1px solid rgba(37, 99, 235, 0.25);
      }
      .hsk-slide-prev:disabled {
        opacity: 0.25;
        cursor: default;
      }
      @media (max-width: 380px) {
        .hsk-slide-desc .hsk-mock-badge { display: none; }
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
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.07);
        border-radius: 20px;
        box-shadow:
          0 8px 32px rgba(0, 0, 0, 0.10),
          0 1px 4px rgba(0, 0, 0, 0.06);
        padding: 42px 45px 33px;
        max-width: 570px;
        min-width: 450px;
      }
      .driver-popover.hsk-tour-popover .driver-popover-title {
        font-family: 'Onest', 'Inter', sans-serif;
        font-size: 19px;
        font-weight: 700;
        color: #111827;
        margin: 0;
        padding: 0;
        line-height: 1.3;
      }
      .driver-popover.hsk-tour-popover .driver-popover-description {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        line-height: 1.65;
        color: #4b5563;
        margin: 10px 0 0;
        padding: 0;
      }
      .driver-popover.hsk-tour-popover .driver-popover-next-btn {
        background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
        color: #fff;
        padding: 14px 36px;
        border-radius: 50px;
        font-size: 15px;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 20px rgba(96, 165, 250, 0.45);
        transition: box-shadow 0.2s, transform 0.2s;
        white-space: nowrap;
        cursor: pointer;
        text-shadow: none;
        -webkit-font-smoothing: antialiased;
      }
      .driver-popover.hsk-tour-popover .driver-popover-next-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(96, 165, 250, 0.55);
      }
      .driver-popover.hsk-tour-popover .driver-popover-prev-btn {
        background: transparent;
        color: #2563eb;
        padding: 14px 28px;
        border-radius: 50px;
        font-size: 15px;
        font-weight: 600;
        border: 1px solid rgba(37, 99, 235, 0.25);
        transition: background 0.2s, border-color 0.2s;
        white-space: nowrap;
        cursor: pointer;
      }
      .driver-popover.hsk-tour-popover .driver-popover-prev-btn:hover:not(:disabled) {
        background: rgba(37, 99, 235, 0.06);
        border-color: rgba(37, 99, 235, 0.45);
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
        background: #e5e7eb;
        border-radius: 999px;
        overflow: hidden;
      }
      .hsk-progress-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 600;
        color: #9ca3af;
        white-space: nowrap;
        flex-shrink: 0;
      }
      .hsk-progress-fill {
        height: 100%;
        background: #6366f1;
        border-radius: 999px;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
