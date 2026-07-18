(function () {
  function injectStyle() {
    if (document.getElementById('novel-player-style')) return;
    var style = document.createElement('style');
    style.id = 'novel-player-style';
    style.textContent = `
      #novel-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.85);
        z-index: 999999999;
      }
      .novel-scene {
        position: relative;
        width: 100%;
        height: 100%;
        overflow: hidden;
      }
      .novel-skip-btn {
        position: absolute;
        top: 18px;
        right: 18px;
        background: rgba(255, 255, 255, 0.08);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 50px;
        padding: 8px 18px;
        font-family: 'Montserrat', sans-serif;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        z-index: 2;
        transition: background 0.2s;
      }
      .novel-skip-btn:hover {
        background: rgba(255, 255, 255, 0.18);
      }
      .novel-sprite {
        position: absolute;
        bottom: 0;
        height: 74vh;
        max-width: 42vw;
        visibility: hidden;
        pointer-events: none;
      }
      .novel-sprite--left {
        left: 3vw;
      }
      .novel-sprite--right {
        right: 3vw;
      }
      .novel-sprite img {
        height: 100%;
        width: auto;
        display: block;
        filter: drop-shadow(0 12px 26px rgba(0, 0, 0, 0.55));
      }
      @media (min-width: 769px) {
        .novel-sprite--left {
          transform: scale(1.3);
          transform-origin: left bottom;
        }
        .novel-sprite--right {
          transform: scale(1.3);
          transform-origin: right bottom;
        }
      }
      .novel-dialogue-box {
        position: absolute;
        left: 50%;
        bottom: 31vh;
        transform: translateX(-50%);
        width: min(96vw, 988px);
        background: #FFF8E7;
        border: none;
        border-radius: 22px;
        padding: 42px 36px 31px;
        box-sizing: border-box;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45);
      }
      .novel-speaker-row {
        position: absolute;
        top: -22px;
        left: 26px;
        right: 26px;
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .novel-speaker {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 19px;
        color: var(--white, #FFF8E7);
        background: var(--red, #940501);
        padding: 13px 30px;
        border-radius: 50px;
        white-space: nowrap;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        flex-shrink: 0;
      }
      .novel-speaker-line {
        flex: 1;
        height: 1px;
        background: var(--red, #940501);
        opacity: 0.85;
      }
      .novel-speaker-star {
        flex-shrink: 0;
        color: var(--red, #940501);
        font-size: 23px;
        line-height: 1;
      }
      .novel-text {
        font-family: 'Montserrat', sans-serif;
        color: #111111;
        font-size: 20px;
        line-height: 1.6;
      }
      .novel-text--narrative {
        font-style: italic;
        text-align: center;
      }
      .novel-next-btn {
        position: absolute;
        right: 24px;
        bottom: -20px;
        background: var(--red, #940501);
        opacity: 1;
        color: var(--white, #FFF8E7);
        border: none;
        border-radius: 50px;
        padding: 12px 26px;
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.2s;
        z-index: 2;
      }
      .novel-next-btn:hover {
        transform: translateY(-2px);
      }
      @media (max-width: 768px) {
        .novel-sprite {
          height: 62vh;
          max-width: 78vw;
          transform: scale(1.4);
        }
        .novel-sprite--left {
          transform-origin: left bottom;
        }
        .novel-sprite--right {
          right: -10vw;
          transform-origin: right bottom;
        }
        .novel-dialogue-box {
          bottom: 40vh;
          padding: 26px 18px 18px;
        }
        .novel-speaker-row {
          top: -16px;
          left: 14px;
          right: 14px;
        }
        .novel-speaker {
          font-size: 13px;
          padding: 8px 18px;
        }
        .novel-next-btn {
          right: 16px;
          bottom: -16px;
          padding: 10px 20px;
        }
        .novel-text {
          font-size: 16px;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function NovelPlayer(lines, userName, csrfToken, lessonId) {
    this.lines = lines || [];
    this.userName = userName || '';
    this.csrfToken = csrfToken || '';
    this.lessonId = lessonId || null;
    this.idx = 0;
  }

  NovelPlayer.prototype._sub = function (text) {
    if (!text) return text || '';
    return text.split('{{user_name}}').join(this.userName);
  };

  NovelPlayer.prototype.start = function () {
    var overlay = document.getElementById('novel-overlay');
    if (!overlay || !this.lines.length) {
      this._finishToLesson();
      return;
    }

    injectStyle();

    this.idx = 0;
    overlay.style.display = '';
    document.body.style.overflow = 'hidden';

    overlay.innerHTML =
      '<div class="novel-scene">' +
        '<button type="button" class="novel-skip-btn">Пропустить новеллу</button>' +
        '<div class="novel-sprite novel-sprite--left"><img alt=""></div>' +
        '<div class="novel-sprite novel-sprite--right"><img alt=""></div>' +
        '<div class="novel-dialogue-box">' +
          '<div class="novel-speaker-row">' +
            '<span class="novel-speaker"></span>' +
            '<span class="novel-speaker-line"></span>' +
            '<span class="novel-speaker-star">&#10022;</span>' +
          '</div>' +
          '<div class="novel-text"></div>' +
          '<button type="button" class="novel-next-btn">Далее →</button>' +
        '</div>' +
      '</div>';

    this.overlay = overlay;
    this.dialogueBoxEl = overlay.querySelector('.novel-dialogue-box');
    this.speakerRowEl = overlay.querySelector('.novel-speaker-row');
    this.speakerEl = overlay.querySelector('.novel-speaker');
    this.textEl = overlay.querySelector('.novel-text');
    this.spriteLeft = overlay.querySelector('.novel-sprite--left');
    this.spriteRight = overlay.querySelector('.novel-sprite--right');
    this.nextBtn = overlay.querySelector('.novel-next-btn');
    this.skipBtn = overlay.querySelector('.novel-skip-btn');

    var self = this;
    this.nextBtn.addEventListener('click', function () { self._onNext(); });
    this.skipBtn.addEventListener('click', function () { self._onSkip(); });

    this._render();
  };

  NovelPlayer.prototype._render = function () {
    var line = this.lines[this.idx];
    var isLast = this.idx === this.lines.length - 1;

    this.spriteLeft.style.visibility = 'hidden';
    this.spriteRight.style.visibility = 'hidden';
    this.dialogueBoxEl.style.display = '';

    if (line.type === 'narrative') {
      this.speakerRowEl.style.display = 'none';
      this.textEl.classList.add('novel-text--narrative');
      this.textEl.textContent = this._sub(line.text);
    } else {
      this.speakerRowEl.style.display = '';
      this.textEl.classList.remove('novel-text--narrative');
      this.speakerEl.textContent = this._sub(line.speaker);
      this.textEl.textContent = this._sub(line.text);

      if (line.character) {
        var spriteEl = line.character === 'user' ? this.spriteLeft : this.spriteRight;
        var img = spriteEl.querySelector('img');
        img.src = '/static/images/characters/' + line.character + '.png';
        img.alt = this._sub(line.speaker);
        spriteEl.style.visibility = 'visible';
      }
    }

    this.nextBtn.textContent = isLast ? 'Начать урок' : 'Далее →';
  };

  NovelPlayer.prototype._onNext = function () {
    var isLast = this.idx === this.lines.length - 1;
    if (isLast) {
      this._markSeen();
      this._finishToLesson();
      return;
    }
    this.idx++;
    this._render();
  };

  NovelPlayer.prototype._onSkip = function () {
    var self = this;
    this._markSeen();
    fetch('/user/skip-novel', {
      method: 'POST',
      headers: { 'X-CSRFToken': this.csrfToken },
    }).finally(function () {
      self._finishToLesson();
    });
  };

  NovelPlayer.prototype._markSeen = function () {
    if (!this.lessonId) return;
    fetch('/dashboard/lessons/' + this.lessonId + '/mark-novel-seen', {
      method: 'POST',
      headers: { 'X-CSRFToken': this.csrfToken },
    });
  };

  NovelPlayer.prototype._finishToLesson = function () {
    var overlay = document.getElementById('novel-overlay');
    var content = document.getElementById('lesson-content');
    if (overlay) overlay.style.display = 'none';
    if (content) content.style.display = '';
    document.body.style.overflow = '';
  };

  window.NovelPlayer = NovelPlayer;
})();
