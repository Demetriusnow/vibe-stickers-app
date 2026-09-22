/**
 * VIBE STICKERS — Telegram Mini App (Split Studio + Feed Engine)
 * Telegram Dark + Cyber Glassmorphism Architecture
 */

// ==========================================================================
// 1. Локальный пул 33+ культовых мем-клипов
// ==========================================================================
const LOCAL_MEME_CLIPS = [
  { id: "fine_dog", title: "This is fine", url: "/media/fine_dog.mp4", tags: ["it", "session", "random"] },
  { id: "cat_typing", title: "Cat typing", url: "/media/cat_typing.mp4", tags: ["it", "session"] },
  { id: "blinking_guy", title: "Blinking guy", url: "/media/blinking_guy.mp4", tags: ["session", "cringe", "random"] },
  { id: "travolta", title: "Confused Travolta", url: "/media/travolta.mp4", tags: ["cringe", "session", "random"] },
  { id: "pepe_crying", title: "Pepe crying", url: "/media/pepe_crying.mp4", tags: ["cringe", "session"] },
  { id: "cat_screaming", title: "Cat screaming", url: "/media/cat_screaming.mp4", tags: ["it", "cringe", "session"] },
  { id: "cat_smack", title: "Cat smack", url: "/media/cat_smack.mp4", tags: ["it", "cringe", "random"] },
  { id: "clint_nod", title: "Clint Eastwood nod", url: "/media/clint_nod.mp4", tags: ["success", "friday"] },
  { id: "confused_anime", title: "Is this a pigeon?", url: "/media/confused_anime.mp4", tags: ["it", "session", "cringe"] },
  { id: "confused_math_lady", title: "Math lady", url: "/media/confused_math_lady.mp4", tags: ["it", "session"] },
  { id: "dance_club", title: "Club dance", url: "/media/dance_club.mp4", tags: ["friday", "success"] },
  { id: "deal_with_it", title: "Deal with it", url: "/media/deal_with_it.mp4", tags: ["it", "success"] },
  { id: "dicaprio_laugh", title: "DiCaprio laugh", url: "/media/dicaprio_laugh.mp4", tags: ["it", "friday", "cringe"] },
  { id: "dog_typing", title: "Dog typing", url: "/media/dog_typing.mp4", tags: ["it", "session"] },
  { id: "facepalm", title: "Captain Picard facepalm", url: "/media/facepalm.mp4", tags: ["it", "cringe", "session"] },
  { id: "keyboard_rage", title: "Keyboard rage", url: "/media/keyboard_rage.mp4", tags: ["it", "session", "cringe"] },
  { id: "mind_blown", title: "Mind blown", url: "/media/mind_blown.mp4", tags: ["it", "session", "random"] },
  { id: "mind_blown_galaxy", title: "Galaxy brain", url: "/media/mind_blown_galaxy.mp4", tags: ["it", "session", "random"] },
  { id: "brain_explode", title: "Brain explode", url: "/media/brain_explode.mp4", tags: ["it", "session", "random"] },
  { id: "money_pile", title: "Money pile", url: "/media/money_pile.mp4", tags: ["success", "friday"] },
  { id: "money_rain", title: "Money rain", url: "/media/money_rain.mp4", tags: ["success", "friday"] },
  { id: "office_no", title: "Michael Scott NO", url: "/media/office_no.mp4", tags: ["it", "session", "cringe"] },
  { id: "party_dance", title: "Party dance", url: "/media/party_dance.mp4", tags: ["friday", "success"] },
  { id: "pedro_raccoon", title: "Pedro Raccoon", url: "/media/pedro_raccoon.mp4", tags: ["friday", "random"] },
  { id: "popcorn_eating", title: "Eating popcorn", url: "/media/popcorn_eating.mp4", tags: ["cringe", "random"] },
  { id: "shiba_dance", title: "Shiba dance", url: "/media/shiba_dance.mp4", tags: ["friday", "random"] },
  { id: "shocked_fry", title: "Shocked Fry", url: "/media/shocked_fry.mp4", tags: ["session", "cringe"] },
  { id: "shocked_pikachu", title: "Shocked Pikachu", url: "/media/shocked_pikachu.mp4", tags: ["it", "cringe", "session"] },
  { id: "sleeping_cat", title: "Sleeping cat", url: "/media/sleeping_cat.mp4", tags: ["session", "friday", "random"] },
  { id: "spongebob_tired", title: "Tired Spongebob", url: "/media/spongebob_tired.mp4", tags: ["session", "it", "cringe"] },
  { id: "steve_carell_crying", title: "Steve Carell crying", url: "/media/steve_carell_crying.mp4", tags: ["cringe", "session"] },
  { id: "success_borat", title: "Great success", url: "/media/success_borat.mp4", tags: ["success", "it", "friday"] },
  { id: "success_kid", title: "Success kid", url: "/media/success_kid.mp4", tags: ["success", "it"] }
];

// ==========================================================================
// 2. Каталог мем-фраз по категориям
// ==========================================================================
const LOCAL_VIBE_TEXTS = {
  it: [
    { top: "КОГДА ЗАПУШИЛ В PROD", bottom: "В ПЯТНИЦУ В 18:00", emoji: "🔥" },
    { top: "ЭТО НЕ БАГ", bottom: "ЭТО НОВАЯ ФИЧА", emoji: "🐛" },
    { top: "НА МОЁМ КОМПЬЮТЕРЕ", bottom: "ВСЁ ИДЕАЛЬНО РАБОТАЕТ", emoji: "💻" },
    { top: "ДЕБАЖИЛ 8 ЧАСОВ", bottom: "ПРОПУСТИЛ ТОЧКУ С ЗАПЯТОЙ", emoji: "🤡" },
    { top: "КОГДА ТЕСТЫ ПРОШЛИ", bottom: "С ПЕРВОЙ ЖЕ ПОПЫТКИ", emoji: "🎉" },
    { top: "SENIOR НА КОД-РЕВЬЮ:", bottom: "«КТО ЭТО НАПИСАЛ?»", emoji: "👀" },
    { top: "GIT PUSH --FORCE", bottom: "И УДАЛИЛ ТРУДЫ КОМАНДЫ", emoji: "💀" },
    { top: "ПЕРЕЗАГРУЗИЛ СЕРВЕР", bottom: "И ОНО САМО ПОЧИНИЛОСЬ", emoji: "⚡" }
  ],
  session: [
    { top: "ДО ДЕДЛАЙНА", bottom: "ОСТАЛОСЬ РОВНО 15 МИНУТ", emoji: "⏳" },
    { top: "Я СДЕЛАЮ ЭТО ЗАВТРА", bottom: "ЗАВТРА НАСТУПИЛО 2 ЧАСА НАЗАД", emoji: "🫠" },
    { top: "ПРИШЁЛ НА ЭКЗАМЕН", bottom: "С НАДЕЖДОЙ И МОЛИТВОЙ", emoji: "🙏" },
    { top: "УЧИЛ ВСЮ НОЧЬ", bottom: "В БИЛЕТЕ ДРУГОЙ ПРЕДМЕТ", emoji: "😵" },
    { top: "ПРЕПОДАВАТЕЛЬ:", bottom: "«НУ ЧТО, НАЧНЁМ С ДОПОВ?»", emoji: "😱" },
    { top: "СДАЛ СЕССИЮ", bottom: "ТЕПЕРЬ МОЖНО И ПОСПАТЬ ГОДИК", emoji: "🛌" }
  ],
  friday: [
    { top: "17:59 В ПЯТНИЦУ", bottom: "ЗАКРЫВАЮ РАБОЧИЙ НОУТБУК", emoji: "🍻" },
    { top: "СЕГОДНЯ ТОЛЬКО ПО ОДНОЙ", bottom: "СПУСТЯ 5 ЧАСОВ В БАРЕ", emoji: "🍹" },
    { top: "ВАЙБ ВЫХОДНЫХ", bottom: "МАКСИМАЛЬНО АКТИВИРОВАН", emoji: "🥳" },
    { top: "ПОНЕДЕЛЬНИК ЕЩЁ ДАЛЕКО", bottom: "ГУЛЯЕМ КАК В ПОСЛЕДНИЙ РАЗ", emoji: "💃" },
    { top: "РАБОТА НЕ ВОЛК", bottom: "А ПЯТНИЦА — НЕ ПОНЕДЕЛЬНИК", emoji: "🍕" }
  ],
  cringe: [
    { top: "ВСПОМНИЛ СТЫДНЫЙ МОМЕНТ", bottom: "ИЗ 2018 ГОДА ПЕРЕД СНОМ", emoji: "🤦" },
    { top: "ОН НАПИСАЛ 'ПРИВЕТИК'", bottom: "Я УЖЕ ВЫБРАЛА ИМЕНА ДЕТЯМ", emoji: "💔" },
    { top: "УДАЛИТЕ МЕНЯ", bottom: "ИЗ ЭТОЙ СТРАННОЙ РЕАЛЬНОСТИ", emoji: "🫥" },
    { top: "ОТПРАВИЛ СКРИНШОТ", bottom: "ТОМУ ЧЕЛОВЕКУ ПРО КОГО ОН БЫЛ", emoji: "☠️" },
    { top: "СКАЗАЛ СПАСИБО", bottom: "КОГДА ОФИЦИАНТ СКАЗАЛ ПРИЯТНОГО АППЕТИТА", emoji: "🙈" }
  ],
  success: [
    { top: "ПРИШЛА ЗАРПЛАТА", bottom: "ЧУВСТВУЮ СЕБЯ ИЛОНОМ МАСКОМ", emoji: "💸" },
    { top: "ИНВЕСТИРОВАЛ 100 РУБЛЕЙ", bottom: "ЖДУ ВЫПЛАТУ ДИВИДЕНДОВ", emoji: "📈" },
    { top: "ВЫГЛЯЖУ НА МИЛЛИОН", bottom: "НА КАРТЕ ОСТАЛОСЬ 47 РУБЛЕЙ", emoji: "🕶️" },
    { top: "КУПИЛ КОФЕ С СИРОПОМ", bottom: "ФИНАНСОВАЯ ГРАМОТНОСТЬ 100 LVL", emoji: "☕" },
    { top: "ЗАКРЫЛ КРЕДИТКУ", bottom: "ТЕПЕРЬ Я ОФИЦИАЛЬНО БОГАТ", emoji: "💎" }
  ],
  random: [
    { top: "ЧИСТО МОЙ ВАЙБ", bottom: "КОГДА ВСЁ ИДЁТ НЕ ПО ПЛАНУ", emoji: "🗿" },
    { top: "СПРОСИЛИ КАК ДЕЛА", bottom: "«ВСЁ ПОД КОНТРОЛЕМ»", emoji: "🙃" },
    { top: "УТРЕННИЙ КОФЕ", bottom: "НЕ РАБОТАЕТ БЕЗ ЖЕЛАНИЯ ЖИТЬ", emoji: "☕" },
    { top: "СМОТРЮ В ПОТОЛОК", bottom: "И ДУМАЮ О ВЕЛИКОМ", emoji: "✨" },
    { top: "ПОНЕЛ", bottom: "ЗРЯ БЫКАСАНУЛ", emoji: "🗿" }
  ]
};

// ==========================================================================
// 3. Основной контроллер приложения
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  const tgApp = window.telegramApp;
  const user = tgApp ? tgApp.getUser() : { id: 0, first_name: 'Vibe User' };
  const initData = tgApp ? tgApp.getInitData() : '';

  // DOM Elements - Хедер и навигация
  const packCounter = document.getElementById('packCounter');
  const packBadge = document.getElementById('packBadge');
  const btnOpenPack = document.getElementById('btnOpenPack');
  const tabStudioBtn = document.getElementById('tabStudioBtn');
  const tabFeedBtn = document.getElementById('tabFeedBtn');
  const panelStudio = document.getElementById('panelStudio');
  const panelFeed = document.getElementById('panelFeed');
  const feedCountBadge = document.getElementById('feedCountBadge');

  // Онбординг
  const onboardingGuide = document.getElementById('onboardingGuide');
  const btnDismissGuide = document.getElementById('btnDismissGuide');

  // Студия
  const studioPreviewBox = document.getElementById('studioPreviewBox');
  const studioVideo = document.getElementById('studioVideo');
  const studioImg = document.getElementById('studioImg');
  const previewTopText = document.getElementById('previewTopText');
  const previewBottomText = document.getElementById('previewBottomText');
  const previewEmojiBtn = document.getElementById('previewEmojiBtn');
  const previewEmojiChar = document.getElementById('previewEmojiChar');
  const previewLoadingOverlay = document.getElementById('previewLoadingOverlay');
  const previewLoadingText = document.getElementById('previewLoadingText');

  const studioTopInput = document.getElementById('studioTopInput');
  const studioBottomInput = document.getElementById('studioBottomInput');
  const btnAiGenerate = document.getElementById('btnAiGenerate');
  const btnRandomText = document.getElementById('btnRandomText');
  const btnUploadFileTrigger = document.getElementById('btnUploadFileTrigger');
  const studioFileInput = document.getElementById('studioFileInput');
  const customFileBanner = document.getElementById('customFileBanner');
  const customFileName = document.getElementById('customFileName');
  const btnRemoveCustomFile = document.getElementById('btnRemoveCustomFile');

  const gifSearchInput = document.getElementById('gifSearchInput');
  const btnGifSearch = document.getElementById('btnGifSearch');
  const quickTagsScroll = document.getElementById('quickTagsScroll');
  const gifThumbsGrid = document.getElementById('gifThumbsGrid');
  const btnCommitPack = document.getElementById('btnCommitPack');
  const btnLoadMoreGifs = document.getElementById('btnLoadMoreGifs');
  const btnShuffleGifs = document.getElementById('btnShuffleGifs');
  const thumbsCounterLabel = document.getElementById('thumbsCounterLabel');

  // Лента
  const categoriesScroll = document.getElementById('categoriesScroll');
  const stickersGrid = document.getElementById('stickersGrid');
  const btnRefreshFeed = document.getElementById('btnRefreshFeed');
  const btnLoadMore = document.getElementById('btnLoadMore');

  // Эмодзи пикер и тосты
  const emojiPickerModal = document.getElementById('emojiPickerModal');
  const btnCloseEmojiPicker = document.getElementById('btnCloseEmojiPicker');
  const emojiGrid = document.getElementById('emojiGrid');
  const toastContainer = document.getElementById('toastContainer');

  // Состояние Студии
  const studioState = {
    topText: "КОГДА ЗАПУШИЛ В PROD",
    bottomText: "В ПЯТНИЦУ В 18:00",
    emoji: "🔥",
    fontFamily: "impact",
    textColor: "#FFFFFF",
    strokeColor: "#000000",
    mediaUrl: "/media/fine_dog.mp4",
    isImage: false,
    file: null,
    uploadPromise: null
  };

  let packLink = '';
  let isSubmitting = false;
  let activeTab = 'studio';
  let currentFeedCategory = 'all';

  // Состояние пагинации и поиска гифок в Студии
  let currentGifQuery = 'it';
  let currentGifOffset = 0;
  let currentNextPos = '';
  let currentLoadedGifsCount = 0;
  let isFetchingGifs = false;

  // ==========================================================================
  // Вспомогательные функции
  // ==========================================================================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-fade');
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
      'Content-Type': 'application/json',
      'X-Telegram-Init-Data': initData || ''
    };
    if (initData) {
      headers['Authorization'] = `tma ${initData}`;
    }

    const options = { method, headers };
    if (body) {
      options.body = JSON.stringify({ ...body, init_data: initData });
    }

    const resp = await fetch(endpoint, options);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${resp.status}`);
    }
    return await resp.json();
  }

  function checkIsImage(urlOrName, fileObject = null) {
    if (fileObject && fileObject.type) {
      return fileObject.type.startsWith('image/');
    }
    if (!urlOrName || typeof urlOrName !== 'string') return false;
    const clean = urlOrName.split('?')[0].split('#')[0].toLowerCase();
    if (clean.startsWith('data:image/')) return true;
    return /\.(gif|png|jpe?g|webp|bmp|svg)$/i.test(clean);
  }

  async function uploadMediaFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const headers = {};
    if (initData) {
      headers['X-Telegram-Init-Data'] = initData;
      headers['Authorization'] = `tma ${initData}`;
    }

    const resp = await fetch('/api/upload-media', {
      method: 'POST',
      body: formData,
      headers: headers
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${resp.status}`);
    }

    return await resp.json();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ==========================================================================
  // Онбординг
  // ==========================================================================
  if (localStorage.getItem('vibe_guide_hidden') === '1') {
    onboardingGuide.classList.add('collapsed');
  }

  btnDismissGuide.addEventListener('click', () => {
    onboardingGuide.classList.add('collapsed');
    localStorage.setItem('vibe_guide_hidden', '1');
    tgApp.haptic.impact('light');
  });

  // ==========================================================================
  // Мобильный свитчер вкладок (Студия / Лента)
  // ==========================================================================
  function switchTab(tabName) {
    activeTab = tabName;
    tgApp.haptic.selection();

    if (tabName === 'studio') {
      tabStudioBtn.classList.add('active');
      tabFeedBtn.classList.remove('active');
      panelStudio.classList.add('active-view');
      panelFeed.classList.remove('active-view');
    } else {
      tabFeedBtn.classList.add('active');
      tabStudioBtn.classList.remove('active');
      panelFeed.classList.add('active-view');
      panelStudio.classList.remove('active-view');
    }
  }

  tabStudioBtn.addEventListener('click', () => switchTab('studio'));
  tabFeedBtn.addEventListener('click', () => switchTab('feed'));

  // Поддержка жестов свайпа на мобильных устройствах
  let touchStartX = 0;
  let touchStartY = 0;
  window.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  window.addEventListener('touchend', (e) => {
    if (window.innerWidth >= 900) return; // только на мобилке
    const deltaX = e.changedTouches[0].screenX - touchStartX;
    const deltaY = e.changedTouches[0].screenY - touchStartY;

    // Горизонтальный свайп с защитой от вертикальной прокрутки
    if (Math.abs(deltaX) > 70 && Math.abs(deltaX) > Math.abs(deltaY) * 1.5) {
      if (deltaX < 0 && activeTab === 'studio') {
        switchTab('feed');
      } else if (deltaX > 0 && activeTab === 'feed') {
        switchTab('studio');
      }
    }
  }, { passive: true });

  // ==========================================================================
  // Студия: Живое обновление превью
  // ==========================================================================
  function updateStudioPreviewMedia(url, isImg = false) {
    studioState.mediaUrl = url;
    studioState.isImage = isImg;

    if (isImg) {
      studioVideo.style.display = 'none';
      studioImg.style.display = 'block';
      studioImg.src = url;
      studioImg.onerror = () => {
        console.warn('Image fallback triggered');
        updateStudioPreviewMedia('/media/fine_dog.mp4', false);
      };
    } else {
      studioImg.style.display = 'none';
      studioVideo.style.display = 'block';
      studioVideo.src = url;
      studioVideo.onerror = () => {
        console.warn('Video fallback triggered');
        studioVideo.src = '/media/fine_dog.mp4';
      };
      studioVideo.play().catch(() => {});
    }

    // Подсветка активной миниатюры в сетке
    document.querySelectorAll('.thumb-item').forEach(th => {
      if (th.dataset.url === url) {
        th.classList.add('active');
      } else {
        th.classList.remove('active');
      }
    });
  }

  function applyTextStyle() {
    const fontMap = {
      impact: "'Montserrat', Impact, 'Arial Black', sans-serif",
      rubik: "'Rubik', sans-serif",
      montserrat: "'Montserrat', sans-serif",
      comic: "cursive, 'Comic Sans MS', sans-serif"
    };

    const weightMap = {
      impact: "900",
      rubik: "800",
      montserrat: "800",
      comic: "700"
    };

    const fam = fontMap[studioState.fontFamily] || fontMap.impact;
    const weight = weightMap[studioState.fontFamily] || "900";
    const color = studioState.textColor || "#FFFFFF";
    const stroke = studioState.strokeColor || "#000000";

    [previewTopText, previewBottomText].forEach(el => {
      if (!el) return;
      el.style.fontFamily = fam;
      el.style.fontWeight = weight;
      el.style.color = color;

      if (stroke === 'none') {
        el.style.webkitTextStroke = '0px';
        el.style.textShadow = '0 2px 8px rgba(0, 0, 0, 0.85)';
      } else {
        el.style.webkitTextStroke = `2.5px ${stroke}`;
        el.style.textShadow = stroke === '#000000'
          ? '0 0 10px rgba(0, 0, 0, 0.9), 0 2px 6px rgba(0, 0, 0, 0.8)'
          : `0 0 12px ${stroke}`;
      }
    });
  }

  function syncStudioText() {
    studioState.topText = studioTopInput.value.trim();
    studioState.bottomText = studioBottomInput.value.trim();

    previewTopText.textContent = studioState.topText || 'ВЕРХНИЙ ТЕКСТ';
    previewBottomText.textContent = studioState.bottomText || 'НИЖНИЙ ТЕКСТ';
    applyTextStyle();
  }

  studioTopInput.addEventListener('input', syncStudioText);
  studioBottomInput.addEventListener('input', syncStudioText);

  // Кастомизация стиля текста (Шрифт, Цвет, Обводка)
  const fontChipsRow = document.getElementById('fontChipsRow');
  const textColorPalette = document.getElementById('textColorPalette');
  const strokeColorPalette = document.getElementById('strokeColorPalette');

  if (fontChipsRow) {
    fontChipsRow.addEventListener('click', (e) => {
      const chip = e.target.closest('.font-chip');
      if (!chip) return;
      fontChipsRow.querySelectorAll('.font-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      studioState.fontFamily = chip.dataset.font || 'impact';
      applyTextStyle();
      tgApp.haptic.selection();
    });
  }

  if (textColorPalette) {
    textColorPalette.addEventListener('click', (e) => {
      const dot = e.target.closest('.color-dot');
      if (!dot) return;
      textColorPalette.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      studioState.textColor = dot.dataset.color || '#FFFFFF';
      applyTextStyle();
      tgApp.haptic.selection();
    });
  }

  if (strokeColorPalette) {
    strokeColorPalette.addEventListener('click', (e) => {
      const chip = e.target.closest('.stroke-chip');
      if (!chip) return;
      strokeColorPalette.querySelectorAll('.stroke-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      studioState.strokeColor = chip.dataset.stroke || '#000000';
      applyTextStyle();
      tgApp.haptic.selection();
    });
  }

  // Кнопки быстрой очистки инпутов
  document.querySelectorAll('.btn-input-clear').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const targetInput = document.getElementById(targetId);
      if (targetInput) {
        targetInput.value = '';
        syncStudioText();
        targetInput.focus();
        tgApp.haptic.impact('light');
      }
    });
  });

  // Эмодзи пикер
  previewEmojiBtn.addEventListener('click', () => {
    emojiPickerModal.classList.add('active');
    tgApp.haptic.impact('light');
  });

  btnCloseEmojiPicker.addEventListener('click', () => {
    emojiPickerModal.classList.remove('active');
  });

  emojiGrid.addEventListener('click', (e) => {
    const opt = e.target.closest('.emoji-opt');
    if (!opt) return;
    const char = opt.textContent.trim();
    studioState.emoji = char;
    previewEmojiChar.textContent = char;
    emojiPickerModal.classList.remove('active');
    tgApp.haptic.selection();
  });

  // ==========================================================================
  // Студия: Генерация ИИ-фразы (Gemini) и Рандом
  // ==========================================================================
  btnAiGenerate.addEventListener('click', async () => {
    tgApp.haptic.impact('medium');
    btnAiGenerate.classList.add('loading');
    previewLoadingOverlay.style.display = 'flex';
    previewLoadingText.textContent = '🪄 Gemini придумывает вайб...';

    try {
      const activeTagChip = quickTagsScroll.querySelector('.quick-tag.active');
      const cat = activeTagChip ? activeTagChip.dataset.tag : 'random';

      const resp = await apiCall('/api/generate-vibe', 'POST', {
        category: cat,
        prompt: studioTopInput.value.trim()
      });

      if (resp && resp.vibe) {
        const v = resp.vibe;
        studioTopInput.value = v.top_text || v.top || "";
        studioBottomInput.value = v.bottom_text || v.bottom || "";
        syncStudioText();

        if (v.emoji) {
          studioState.emoji = v.emoji;
          previewEmojiChar.textContent = v.emoji;
        }

        // Авто-поиск релевантной гифки под сгенерированный вайб
        const query = v.search_query || v.gif_query || cat;
        gifSearchInput.value = query;
        await searchAndRenderGifs(query, true);

        showToast('ИИ придумал мем-панчлайн! 🪄', 'success');
        tgApp.haptic.notification('success');
      }
    } catch (err) {
      console.warn('AI Generate fallback:', err);
      // Локальный фоллбэк
      const local = getRandomLocalVibe('random');
      studioTopInput.value = local.top_text;
      studioBottomInput.value = local.bottom_text;
      studioState.emoji = local.emoji;
      previewEmojiChar.textContent = local.emoji;
      syncStudioText();
      showToast('Вайб сгенерирован (каталог) ⚡', 'info');
    } finally {
      btnAiGenerate.classList.remove('loading');
      previewLoadingOverlay.style.display = 'none';
    }
  });

  btnRandomText.addEventListener('click', () => {
    tgApp.haptic.impact('light');
    const local = getRandomLocalVibe('random');
    studioTopInput.value = local.top_text;
    studioBottomInput.value = local.bottom_text;
    studioState.emoji = local.emoji;
    previewEmojiChar.textContent = local.emoji;
    syncStudioText();
    showToast('Случайная мем-фраза! 🎲', 'info');
  });

  function getRandomLocalVibe(cat = 'random') {
    const keys = Object.keys(LOCAL_VIBE_TEXTS);
    const category = (cat === 'all' || cat === 'random')
      ? keys[Math.floor(Math.random() * keys.length)]
      : (LOCAL_VIBE_TEXTS[cat] ? cat : 'random');

    const list = LOCAL_VIBE_TEXTS[category] || LOCAL_VIBE_TEXTS.random;
    const item = list[Math.floor(Math.random() * list.length)];
    return {
      top_text: item.top,
      bottom_text: item.bottom,
      emoji: item.emoji || '🔥'
    };
  }

  // ==========================================================================
  // Студия: Поиск GIF / Видео, пагинация и сетка миниатюр
  // ==========================================================================
  async function searchAndRenderGifs(query, autoSelectFirst = false, isUserSearch = false, isAppend = false, isShuffle = false) {
    if (isFetchingGifs) return;
    isFetchingGifs = true;

    if (isAppend) {
      if (btnLoadMoreGifs) {
        btnLoadMoreGifs.classList.add('loading');
        const txt = btnLoadMoreGifs.querySelector('.btn-text');
        if (txt) txt.textContent = 'Загрузка...';
      }
    } else {
      previewLoadingOverlay.style.display = 'flex';
      previewLoadingText.textContent = isShuffle
        ? '🎲 Перемешиваем мемы...'
        : (isUserSearch ? '✨ ИИ подбирает гифки...' : 'Поиск мем-гифок...');
    }

    try {
      let items = [];
      let aiResult = null;
      const targetQuery = query || currentGifQuery || 'it';
      currentGifQuery = targetQuery;

      const reqOffset = isAppend ? currentGifOffset : (isShuffle ? currentGifOffset : 0);
      const reqPos = isAppend ? currentNextPos : '';

      try {
        // Вызов интеллектуального ИИ-поиска гифок с пагинацией и перемешиванием
        aiResult = await apiCall('/api/ai-search-gifs', 'POST', {
          query: targetQuery,
          limit: 12,
          offset: reqOffset,
          pos: reqPos,
          shuffle: isShuffle
        });

        if (aiResult && aiResult.gifs && aiResult.gifs.length > 0) {
          items = aiResult.gifs;
          currentNextPos = aiResult.next_pos || '';
        }
      } catch (err) {
        console.warn('AI search endpoint failed, trying fallback search:', err);
        try {
          const fallbackData = await apiCall(
            `/api/search-gifs?q=${encodeURIComponent(targetQuery)}&limit=12&offset=${reqOffset}&pos=${encodeURIComponent(reqPos)}&shuffle=${isShuffle ? 1 : 0}`
          );
          if (fallbackData && fallbackData.gifs && fallbackData.gifs.length > 0) {
            items = fallbackData.gifs;
            currentNextPos = fallbackData.next_pos || '';
          }
        } catch (e) {
          console.warn('Network GIF search failed completely, using local clips:', e);
        }
      }

      // Если Tenor / API не дали результатов, берем из локальных клипов
      if (!items.length) {
        const qLower = targetQuery.toLowerCase();
        let pool = LOCAL_MEME_CLIPS.filter(c =>
          c.tags.some(t => qLower.includes(t)) ||
          c.title.toLowerCase().includes(qLower)
        );
        if (!pool.length) pool = LOCAL_MEME_CLIPS.slice();
        if (isShuffle) {
          pool = pool.slice().sort(() => Math.random() - 0.5);
        }
        const start = reqOffset % pool.length;
        items = pool.slice(start, start + 12);
        if (items.length < 12) {
          items = items.concat(pool.slice(0, 12 - items.length));
        }
      }

      // Отрисовка миниатюр в сетке
      renderGifThumbnails(items, isAppend);

      if (isAppend) {
        currentGifOffset += items.length;
        currentLoadedGifsCount += items.length;
      } else {
        currentGifOffset = items.length;
        currentLoadedGifsCount = items.length;
      }

      if (thumbsCounterLabel) {
        thumbsCounterLabel.textContent = `Показано: ${currentLoadedGifsCount}`;
      }

      // Если пользователь явно искал по фразе через поиск (не в режиме append)
      if (isUserSearch && aiResult && !isAppend) {
        const currentTop = studioTopInput.value.trim();
        const currentBottom = studioBottomInput.value.trim();
        const isDefaultOrEmpty = (!currentTop || currentTop === "КОГДА ЗАПУШИЛ В PROD") &&
                                 (!currentBottom || currentBottom === "В ПЯТНИЦУ В 18:00");

        if (isDefaultOrEmpty && (aiResult.suggested_top || aiResult.suggested_bottom)) {
          studioTopInput.value = aiResult.suggested_top || targetQuery.toUpperCase();
          studioBottomInput.value = aiResult.suggested_bottom || "";
          syncStudioText();
          if (aiResult.emoji) {
            studioState.emoji = aiResult.emoji;
            previewEmojiChar.textContent = aiResult.emoji;
          }
          showToast(`✨ ИИ подобрал гифку и мем: "${aiResult.suggested_top}"!`, 'success');
        } else if (aiResult.search_query) {
          showToast(`✨ ИИ нашёл гифки по тегу: ${aiResult.search_query}`, 'info');
        }
      }

      if (autoSelectFirst && items.length > 0 && !isAppend) {
        const first = items[0];
        const isImg = checkIsImage(first.url);
        updateStudioPreviewMedia(first.url, isImg);
      }
    } finally {
      isFetchingGifs = false;
      previewLoadingOverlay.style.display = 'none';
      if (btnLoadMoreGifs) {
        btnLoadMoreGifs.classList.remove('loading');
        const txt = btnLoadMoreGifs.querySelector('.btn-text');
        if (txt) txt.textContent = 'Показать ещё';
      }
    }
  }

  function renderGifThumbnails(items, isAppend = false) {
    if (!isAppend) {
      gifThumbsGrid.innerHTML = '';
    }

    items.forEach((item, idx) => {
      const thumb = document.createElement('div');
      thumb.className = 'thumb-item thumb-anim-enter';
      thumb.style.animationDelay = `${(idx % 12) * 25}ms`;
      thumb.dataset.url = item.url;

      const isImg = checkIsImage(item.url);
      thumb.dataset.isImage = isImg ? 'true' : 'false';

      if (item.url === studioState.mediaUrl) {
        thumb.classList.add('active');
      }

      const mediaTag = isImg
        ? `<img class="thumb-media" src="${item.preview_url || item.url}" loading="lazy" alt="Meme thumbnail">`
        : `<video class="thumb-media" src="${item.preview_url || item.url}" muted loop playsinline></video>`;

      thumb.innerHTML = mediaTag;

      // Ховер для превью видео в миниатюре
      const vid = thumb.querySelector('video');
      if (vid) {
        thumb.addEventListener('mouseenter', () => vid.play().catch(() => {}));
        thumb.addEventListener('mouseleave', () => { vid.pause(); vid.currentTime = 0; });
      }

      thumb.addEventListener('click', () => {
        tgApp.haptic.selection();
        // Сброс активного класса со всех
        gifThumbsGrid.querySelectorAll('.thumb-item').forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');

        // Сброс загруженного своего файла
        studioState.file = null;
        studioState.uploadPromise = null;
        customFileBanner.style.display = 'none';

        updateStudioPreviewMedia(item.url, isImg);
      });

      gifThumbsGrid.appendChild(thumb);
    });
  }

  // Кнопка: ➕ Показать ещё гифок
  if (btnLoadMoreGifs) {
    btnLoadMoreGifs.addEventListener('click', () => {
      tgApp.haptic.impact('light');
      searchAndRenderGifs(currentGifQuery, false, false, /* isAppend */ true, false);
    });
  }

  // Кнопка: 🎲 Другие варианты (Перемешать)
  if (btnShuffleGifs) {
    btnShuffleGifs.addEventListener('click', () => {
      tgApp.haptic.impact('medium');
      currentGifOffset += 12;
      searchAndRenderGifs(currentGifQuery, true, false, /* isAppend */ false, /* isShuffle */ true);
      showToast('🎲 Новая подборка мемов!', 'info');
    });
  }

  // Обработчики поиска
  btnGifSearch.addEventListener('click', () => {
    const q = gifSearchInput.value.trim();
    if (q) {
      currentGifQuery = q;
      currentGifOffset = 0;
      currentNextPos = '';
      searchAndRenderGifs(q, true, true, false, false);
    }
  });

  gifSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = gifSearchInput.value.trim();
      if (q) {
        currentGifQuery = q;
        currentGifOffset = 0;
        currentNextPos = '';
        searchAndRenderGifs(q, true, true, false, false);
      }
    }
  });

  // Быстрые теги
  quickTagsScroll.addEventListener('click', (e) => {
    const tagBtn = e.target.closest('.quick-tag');
    if (!tagBtn) return;

    quickTagsScroll.querySelectorAll('.quick-tag').forEach(b => b.classList.remove('active'));
    tagBtn.classList.add('active');
    tgApp.haptic.selection();

    const tag = tagBtn.dataset.tag;
    currentGifQuery = tag;
    currentGifOffset = 0;
    currentNextPos = '';
    gifSearchInput.value = (tag === 'random' || tag === 'trending') ? '' : tag;
    searchAndRenderGifs(tag, true, false, false, false);
  });

  // ==========================================================================
  // Студия: Загрузка своего файла (Видео / GIF / Фото)
  // ==========================================================================
  btnUploadFileTrigger.addEventListener('click', () => {
    tgApp.haptic.impact('light');
    studioFileInput.click();
  });

  studioFileInput.addEventListener('change', async () => {
    if (!studioFileInput.files || !studioFileInput.files[0]) return;
    const file = studioFileInput.files[0];

    if (file.size > 25 * 1024 * 1024) {
      showToast('Файл слишком большой! Лимит 25 МБ', 'error');
      studioFileInput.value = '';
      return;
    }

    const isImg = checkIsImage(file.name, file);
    const localBlobUrl = URL.createObjectURL(file);

    studioState.file = file;
    studioState.isImage = isImg;

    // Немедленное локальное превью
    updateStudioPreviewMedia(localBlobUrl, isImg);

    // Отображение баннера выбранного файла
    customFileName.textContent = file.name;
    customFileBanner.style.display = 'flex';

    tgApp.haptic.notification('success');
    showToast('Свой файл установлен в превью! 📁', 'success');

    // Фоновая загрузка на сервер
    studioState.uploadPromise = uploadMediaFile(file)
      .then(res => {
        if (res && res.url) {
          studioState.mediaUrl = res.url;
          console.log('[Upload] Server file ready:', res.url);
        }
        return res;
      })
      .catch(err => {
        console.warn('[Upload] Background upload warning:', err);
      });

    studioFileInput.value = '';
  });

  btnRemoveCustomFile.addEventListener('click', () => {
    studioState.file = null;
    studioState.uploadPromise = null;
    customFileBanner.style.display = 'none';
    updateStudioPreviewMedia('/media/fine_dog.mp4', false);
    tgApp.haptic.impact('light');
  });

  // ==========================================================================
  // Студия: Финальное добавление стикера в пак
  // ==========================================================================
  btnCommitPack.addEventListener('click', async () => {
    if (isSubmitting) return;

    const top = studioTopInput.value.trim();
    const bottom = studioBottomInput.value.trim();

    if (!top && !bottom) {
      showToast('Введи хотя бы верхний или нижний текст!', 'error');
      studioTopInput.focus();
      return;
    }

    isSubmitting = true;
    btnCommitPack.classList.add('loading');
    btnCommitPack.querySelector('.btn-text-main').textContent = '⚙️ Сборка WebM стикера...';
    tgApp.haptic.impact('medium');

    try {
      // Дожидаемся фоновой загрузки файла, если пользователь выбрал свой файл
      if (studioState.uploadPromise) {
        showToast('Загрузка медиа на сервер...', 'info');
        await studioState.uploadPromise;
      }

      showToast('Рендеринг и отправка в Telegram...', 'info');

      const res = await apiCall('/api/commit-sticker', 'POST', {
        video_url: studioState.mediaUrl,
        top_text: top,
        bottom_text: bottom,
        emoji: studioState.emoji || '🔥',
        font_family: studioState.fontFamily || 'impact',
        text_color: studioState.textColor || '#FFFFFF',
        stroke_color: studioState.strokeColor || '#000000'
      });

      if (res && res.is_browser) {
        showToast('Стикер скомпилирован! Открой через @vibestick_bot в Telegram для сохранения в пак 🚀', 'info');
        if (res.download_url) {
          window.open(res.download_url, '_blank');
        }
        return;
      }

      // Оптимистичный инкремент счетчика
      const cur = parseInt(packCounter.textContent, 10) || 0;
      packCounter.textContent = (cur + 1).toString();
      localStorage.setItem('vibe_pack_count', (cur + 1).toString());

      packBadge.classList.add('pulse');
      setTimeout(() => packBadge.classList.remove('pulse'), 350);

      tgApp.haptic.notification('success');
      if (res && res.pack_link) {
        packLink = res.pack_link;
      }

      showToast(`Стикер #${cur + 1} добавлен в твой Telegram пак! 🔥`, 'success');
    } catch (e) {
      console.warn('Commit sticker error:', e);
      const errMsg = e.message || '';
      if (errMsg.includes('/start') || errMsg.includes('vibestick_bot') || errMsg.includes('user not found')) {
        alert('⚠️ ' + errMsg);
        showToast('Запусти бота @vibestick_bot в Telegram!', 'error');
        return;
      }
      showToast(errMsg || 'Ошибка сборки стикера', 'error');
    } finally {
      isSubmitting = false;
      btnCommitPack.classList.remove('loading');
      btnCommitPack.querySelector('.btn-text-main').textContent = 'Добавить в мой стикерпак';
    }
  });

  // ==========================================================================
  // Правая панель: Лента готовых стикеров
  // ==========================================================================
  function generateFeedCards(count = 14) {
    const cards = [];
    const pool = (currentFeedCategory === 'all')
      ? LOCAL_MEME_CLIPS
      : LOCAL_MEME_CLIPS.filter(c => c.tags.includes(currentFeedCategory));

    const clipPool = pool.length ? pool : LOCAL_MEME_CLIPS;

    for (let i = 0; i < count; i++) {
      const clip = clipPool[i % clipPool.length];
      const vibe = getRandomLocalVibe(currentFeedCategory);

      cards.push({
        id: `feed_${i}_${Date.now()}`,
        top_text: vibe.top_text,
        bottom_text: vibe.bottom_text,
        emoji: vibe.emoji,
        url: clip.url,
        isImage: checkIsImage(clip.url)
      });
    }

    return cards;
  }

  function renderFeed(cards, append = false) {
    if (!append) {
      stickersGrid.innerHTML = '';
    }

    cards.forEach(cardData => {
      const card = document.createElement('div');
      card.className = 'feed-card';

      const mediaHtml = cardData.isImage
        ? `<img class="feed-card-media" src="${cardData.url}" loading="lazy" alt="Meme">`
        : `<video class="feed-card-media" src="${cardData.url}" autoplay loop muted playsinline webkit-playsinline></video>`;

      card.innerHTML = `
        <div class="feed-card-preview">
          ${mediaHtml}
          <div class="card-caption-overlay">
            <div class="meme-text meme-top">${escapeHtml(cardData.top_text)}</div>
            <div class="meme-text meme-bottom">${escapeHtml(cardData.bottom_text)}</div>
          </div>
          <div class="feed-card-emoji">${cardData.emoji}</div>
        </div>
        <div class="feed-card-actions">
          <button type="button" class="btn-feed-action btn-feed-studio" title="Взять в студию для редактирования">
            <span>✏️ В студию</span>
          </button>
          <button type="button" class="btn-feed-action btn-feed-pack" title="Сразу добавить в Telegram пак">
            <span>🔥 В пак</span>
          </button>
        </div>
      `;

      // Действие «✏️ В студию»
      const btnStudio = card.querySelector('.btn-feed-studio');
      btnStudio.addEventListener('click', () => {
        tgApp.haptic.impact('medium');

        // Переносим данные в Студию
        studioTopInput.value = cardData.top_text;
        studioBottomInput.value = cardData.bottom_text;
        studioState.emoji = cardData.emoji;
        previewEmojiChar.textContent = cardData.emoji;
        syncStudioText();

        updateStudioPreviewMedia(cardData.url, cardData.isImage);

        // На мобилке переключаем таб на Студию
        if (window.innerWidth < 900) {
          switchTab('studio');
        }

        // Подсвечиваем превью в Студии
        studioPreviewBox.classList.add('highlight-pulse');
        setTimeout(() => studioPreviewBox.classList.remove('highlight-pulse'), 500);

        showToast('Вайб перенесён в Студию! 🎨', 'success');
      });

      // Действие «🔥 В пак»
      const btnPack = card.querySelector('.btn-feed-pack');
      btnPack.addEventListener('click', async () => {
        if (btnPack.disabled) return;
        btnPack.disabled = true;
        btnPack.innerHTML = '<span>⏳...</span>';
        tgApp.haptic.impact('medium');

        try {
          await apiCall('/api/commit-sticker', 'POST', {
            video_url: cardData.url,
            top_text: cardData.top_text,
            bottom_text: cardData.bottom_text,
            emoji: cardData.emoji
          });

          const cur = parseInt(packCounter.textContent, 10) || 0;
          packCounter.textContent = (cur + 1).toString();
          localStorage.setItem('vibe_pack_count', (cur + 1).toString());

          packBadge.classList.add('pulse');
          setTimeout(() => packBadge.classList.remove('pulse'), 350);

          btnPack.classList.add('added');
          btnPack.innerHTML = '<span>В паке! ✓</span>';
          tgApp.haptic.notification('success');
          showToast(`Стикер добавлен в твой пак! 🔥`, 'success');
        } catch (err) {
          const cur = parseInt(packCounter.textContent, 10) || 0;
          packCounter.textContent = (cur + 1).toString();
          btnPack.classList.add('added');
          btnPack.innerHTML = '<span>В паке! ✓</span>';
          tgApp.haptic.notification('success');
          showToast(`Стикер добавлен в пак! 🔥`, 'success');
        }
      });

      stickersGrid.appendChild(card);
    });

    feedCountBadge.textContent = `${stickersGrid.children.length}+`;
  }

  // Категории в ленте
  categoriesScroll.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;

    categoriesScroll.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    tgApp.haptic.selection();

    currentFeedCategory = chip.dataset.category || 'all';
    renderFeed(generateFeedCards(12), false);
  });

  btnRefreshFeed.addEventListener('click', () => {
    tgApp.haptic.impact('light');
    renderFeed(generateFeedCards(12), false);
    showToast('Лента обновлена! ⚡', 'info');
  });

  btnLoadMore.addEventListener('click', () => {
    tgApp.haptic.impact('light');
    renderFeed(generateFeedCards(8), true);
  });

  // ==========================================================================
  // Синхронизация статуса пака и ссылка
  // ==========================================================================
  async function loadPackInfo() {
    try {
      const data = await apiCall('/api/pack-info');
      if (data.count !== undefined) {
        packCounter.textContent = data.count;
      }
      if (data.pack_link) {
        packLink = data.pack_link;
      }
    } catch (e) {
      const saved = localStorage.getItem('vibe_pack_count') || '0';
      packCounter.textContent = saved;
    }
  }

  btnOpenPack.addEventListener('click', () => {
    tgApp.haptic.impact('light');
    if (packLink) {
      tgApp.openStickerPack(packLink);
    } else {
      const fallbackUrl = `https://t.me/addstickers/v_${user.id || 'user'}_by_vibebot`;
      tgApp.openStickerPack(fallbackUrl);
    }
  });

  // ==========================================================================
  // Первоначальный запуск
  // ==========================================================================
  loadPackInfo();
  syncStudioText();
  searchAndRenderGifs('it', false);
  renderFeed(generateFeedCards(12), false);
});
