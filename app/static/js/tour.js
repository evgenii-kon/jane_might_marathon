(function () {
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

  if (localStorage.getItem('tour_completed')) return;

  var { driver } = window.driver.js;
  var TOTAL_STEPS = 14;

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
    var pct = Math.round(((idx + 1) / TOTAL_STEPS) * 100);

    // bar inside progress-text
    if (!progressText.querySelector('.hsk-progress-track')) {
      progressText.innerHTML = '<div class="hsk-progress-track"><div class="hsk-progress-fill"></div></div>';
    }
    var fill = progressText.querySelector('.hsk-progress-fill');
    if (fill) fill.style.width = pct + '%';

    // counter injected into footer, between progress-text and prev-btn
    var label = footer.querySelector('.hsk-progress-label');
    if (!label) {
      label = document.createElement('span');
      label.className = 'hsk-progress-label';
      var prevBtn = footer.querySelector('.driver-popover-prev-btn');
      footer.insertBefore(label, prevBtn);
    }
    label.textContent = (idx + 1) + ' / ' + TOTAL_STEPS;
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
    steps: [
      {
        popover: {
          title: 'Добро пожаловать В School Might!',
          description:
            'Это платформа для изучения китайского языка по программе HSK-1. Предлагаем прямо сейчас пройти короткую экскурсию — она займёт меньше минуты и покажет все основные разделы. Мы объясним тебе, как пользоваться платформой, как выстроить свое обучение, чтобы оно было и понятным и эффективным.<br><br>' +
            'Если хотите вернуться к ней позже, её всегда можно запустить снова в разделе «Профиль».',
        },
      },
      {
        element: '#tour-profile',
        popover: {
          title: 'Ваш профиль',
          description:
            'Здесь хранится статистика и прогресс. Можно редактировать данные о себе, а также тут мы можете обучающий тур по платформе.',
          side: 'bottom',
          align: 'end',
        },
      },
      {
        element: '#tour-articles',
        popover: {
          title: 'Статьи',
          description:
            'Здесь собраны полезные материалы о китайском языке и культуре — чтение таких статей помогает лучше понимать восточную культуру.<br><br>' +
            'Читайте эти статьи время от времени — это будет прекрасным дополнением к обучению после изучения теории и грамматики.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#tour-idioms',
        popover: {
          title: 'Идиомы',
          description:
            'Чэнъюй — четырёхсловные идиомы с богатой историей. Знание таких речевых структур серьезно повышает твой навык обращения с языком. Используя их ты дашь собеседнику понять, что ты говоришь как настоящие носители языка.<br><br>' +
            'В этот разделе реализован самоконтроль в изучении материала. Переводите идиомы из раздела «Не знаю», в размер «Знаю хорошо», чтобы не путать уже изученный материал, и тот что еще предстоит пройти.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#tour-grammar',
        popover: {
          title: 'Грамматика',
          description:
            'Здесь хранятся правила и конструкции HSK-1 с примерами и таблицами.<br><br>' +
            'Проходить грамматику ты будешь и на уроках, однако чтобы при желании повторить определенное правило не нужно было искать в текстовых или видео уроках информацию, мы подготовили раздел где коротко описаны все грамматические конструкции с примерами.<br><br>' +
            'А быстро найти нужное правило ты можешь применив фильтрацию по тегам.<br><br>' +
            'Заходи в этот блок для того чтобы закреплять грамматику, уже пройденную на уроках.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#tour-reading',
        popover: {
          title: 'Тексты для чтения',
          description:
            'Короткие тексты на китайском языке с пиньинем и переводом, а после каждого — тест на понимание прочитанного.<br><br>' +
            'Это отличный способ закрепить лексику из уроков в живом контексте. Читай тексты по мере прохождения курса — они подобраны специально из слов HSK-1.',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#tour-trainer',
        popover: {
          title: 'Тренажёр слов',
          description:
            'В этом разделе собраны тренажеры по словам.<br><br>' +
            'В настоящий момент тут есть 2 режима: режим повторения всех слов уровня HSK-1, а также режим ежедневного повторения.<br><br>' +
            'Рекомендуем пользоваться режимом ежедневного повторения регулярно. Тут тебя будут встречать только те слова, которые ты уже прошел на уроках, а также они отбираются ежедневно по системе кривой Эббингауза — система сама понимает, какие слова даются тебе хорошо, а какие необходимо повторить. Это крайне мощная стратегия для запоминания слов!',
          side: 'bottom',
          align: 'start',
        },
      },
      {
        element: '#tour-rating',
        popover: {
          title: 'Рейтинг слов',
          description:
            'В этой вкладке хранится все история твоих ответов в тренажерах. Здесь можно оценить прогресс самостоятельно. Для каждого слова существует Mastery level, который или растет или снижается после правильных/неправильных ответов.<br><br>' +
            'Постирайте достичь максимального уровня по каждому слову!',
          side: 'left',
          align: 'start',
        },
      },
      {
        element: '.activity-section',
        popover: {
          title: 'Активность',
          description:
            'Календарь фиксирует дни занятий и помогает держать streak. Чем больше активности вы проявляете за день — тем более насыщенная становится отметка для в календаре.<br>' +
            'Занимайтесь каждый день, чтобы серия не прерывалась!',
          side: 'right',
          align: 'start',
        },
      },
      {
        element: '#tour-weeks',
        popover: {
          title: 'Недели марафона',
          description:
            'Это основная вкладка, с которой тебе предстоит работать.<br>' +
            'Курс разбит на 6 недель. Каждая открывается последовательно и содержит уроки, слова и упражнения.<br>' +
            'Заходи сюда ежедневно и изучай уроки.',
          side: 'top',
          align: 'start',
        },
      },
      {
        popover: {
          title: 'Так выглядят уроки внутри недели',
          description:
            'Каждый урок — это отдельная карточка. Нажми «Начать», чтобы открыть материал.' +
            '<div style="margin-top:14px;background:#f0f4ff;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #dce6ff;">' +
              '<div style="width:36px;height:36px;border-radius:50%;background:#6b7cff;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
              '<div style="flex:1;">' +
                '<div style="font-weight:700;font-size:14px;color:#1a1a2e;">Историческая лексика</div>' +
                '<div style="font-size:12px;color:#6b7cff;margin-top:2px;">Изучите новую тему</div>' +
                '<div style="font-size:11px;color:#888;margin-top:4px;">📝 Упражнения: 0/4</div>' +
              '</div>' +
              '<div style="background:linear-gradient(135deg,#2563eb,#60a5fa);color:#fff;border-radius:50px;padding:8px 18px;font-size:13px;font-weight:700;white-space:nowrap;">🚀 Начать</div>' +
            '</div>',
        },
      },
      {
        popover: {
          title: 'После теории появляются упражнения',
          description:
            'Как только ты изучишь теорию урока, появится кнопка «Упражнения» — обязательно выполни их для закрепления материала.' +
            '<div style="margin-top:14px;background:#f0f4ff;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #dce6ff;">' +
              '<div style="width:36px;height:36px;border-radius:50%;background:#22c55e;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
              '<div style="flex:1;">' +
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
      },
      {
        popover: {
          title: 'Урок завершён!',
          description:
            'Когда теория изучена и все упражнения выполнены — обе кнопки становятся зелёными и появляется метка «Все выполнены». Так ты отслеживаешь, что уже пройдено.' +
            '<div style="margin-top:14px;background:#f0fff4;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;border:1px solid #bbf7d0;">' +
              '<div style="width:36px;height:36px;border-radius:50%;background:#22c55e;color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">6</div>' +
              '<div style="flex:1;">' +
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
      },
      {
        popover: {
          title: '🚀 Готовы начать?',
          description:
            'Открой первую неделю и сделайте первый шаг навстречу китайскому языку!',
        },
      },
    ],
  });

  setTimeout(function () {
    lockScroll();
    tour.drive();
  }, 800);
})();
