/**
 * Telegram WebApp SDK Integration Module
 * Handles viewport stabilization, theme synchronization, haptic feedback and deeplinks.
 */

class TelegramIntegration {
  constructor() {
    this.tg = window.Telegram?.WebApp || null;
    this.isAvailable = Boolean(this.tg);

    this.init();
  }

  init() {
    if (!this.isAvailable) {
      console.warn('[Telegram Mini App] Telegram WebApp SDK not found. Running in browser/demo mode.');
      this.setupFallbackViewport();
      return;
    }

    try {
      // Сообщаем клиенту Telegram, что приложение готово к отображению
      this.tg.ready();
      this.tg.expand();

      // Отключаем вертикальные свайпы для закрытия шторки (доступно с Bot API 7.7+)
      if (this.tg.isVersionAtLeast && this.tg.isVersionAtLeast('7.7')) {
        this.tg.disableVerticalSwipes();
      }

      // Настройка высоты экрана
      this.bindViewport();

      // Настройка темы оформления Telegram
      this.syncTheme();

      console.log(`[Telegram Mini App] SDK Initialized. Platform: ${this.tg.platform}, Version: ${this.tg.version}`);
    } catch (err) {
      console.error('[Telegram Mini App] Error initializing SDK:', err);
    }
  }

  /**
   * Синхронизация реальной высоты экрана для защиты от 100vh бага на iOS/Android
   */
  bindViewport() {
    const updateHeight = () => {
      const height = this.tg?.viewportStableHeight || window.innerHeight;
      document.documentElement.style.setProperty('--tg-viewport-height', `${height}px`);
    };

    updateHeight();
    this.tg?.onEvent('viewportChanged', updateHeight);
    window.addEventListener('resize', updateHeight);
  }

  setupFallbackViewport() {
    const updateHeight = () => {
      document.documentElement.style.setProperty('--tg-viewport-height', `${window.innerHeight}px`);
    };
    updateHeight();
    window.addEventListener('resize', updateHeight);
  }

  /**
   * Синхронизация CSS переменных с параметрами темы Telegram
   */
  syncTheme() {
    if (!this.tg) return;

    const applyThemeParams = () => {
      const params = this.tg.themeParams;
      if (!params) return;

      const root = document.documentElement;
      if (params.bg_color) root.style.setProperty('--tg-theme-bg-color', params.bg_color);
      if (params.secondary_bg_color) root.style.setProperty('--tg-theme-secondary-bg-color', params.secondary_bg_color);
      if (params.text_color) root.style.setProperty('--tg-theme-text-color', params.text_color);
      if (params.hint_color) root.style.setProperty('--tg-theme-hint-color', params.hint_color);
      if (params.link_color) root.style.setProperty('--tg-theme-link-color', params.link_color);
      if (params.button_color) root.style.setProperty('--tg-theme-button-color', params.button_color);
      if (params.button_text_color) root.style.setProperty('--tg-theme-button-text-color', params.button_text_color);

      document.documentElement.setAttribute('data-color-scheme', this.tg.colorScheme || 'dark');
    };

    applyThemeParams();
    this.tg.onEvent('themeChanged', applyThemeParams);
  }

  /**
   * Тактильный отклик (Haptic Feedback)
   */
  haptic = {
    impact: (style = 'medium') => {
      try {
        if (this.tg?.HapticFeedback?.impactOccurred) {
          this.tg.HapticFeedback.impactOccurred(style);
        } else if ('vibrate' in navigator) {
          navigator.vibrate(style === 'heavy' ? 40 : 20);
        }
      } catch (e) {}
    },

    notification: (type = 'success') => {
      try {
        if (this.tg?.HapticFeedback?.notificationOccurred) {
          this.tg.HapticFeedback.notificationOccurred(type);
        } else if ('vibrate' in navigator) {
          navigator.vibrate(type === 'success' ? [30, 40, 30] : [60, 50, 60]);
        }
      } catch (e) {}
    },

    selection: () => {
      try {
        if (this.tg?.HapticFeedback?.selectionChanged) {
          this.tg.HapticFeedback.selectionChanged();
        } else if ('vibrate' in navigator) {
          navigator.vibrate(10);
        }
      } catch (e) {}
    }
  };

  /**
   * Нативное открытие стикерпака внутри приложения Telegram
   */
  openStickerPack(urlOrShortName) {
    let url = urlOrShortName;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = `https://t.me/addstickers/${urlOrShortName}`;
    }

    console.log('[Telegram Mini App] Opening stickerpack deeplink:', url);

    if (this.tg?.openTelegramLink) {
      this.tg.openTelegramLink(url);
    } else {
      window.open(url, '_blank');
    }
  }

  /**
   * Получение Telegram initData для валидации на сервере
   */
  getInitData() {
    return this.tg?.initData || '';
  }

  /**
   * Получение данных текущего пользователя
   */
  getUser() {
    return this.tg?.initDataUnsafe?.user || {
      id: 0,
      first_name: 'Vibe User',
      username: 'vibeswiper_demo'
    };
  }
}

// Экспорт синглтона в глобальную область видимости
window.telegramApp = new TelegramIntegration();
