/**
 * Swiper Engine Module
 * Robust Tinder-like gesture processor using PointerEvents API.
 * Supports touch, mouse, keyboard shortcuts, and programmatic triggers.
 */

class CardSwiper {
  constructor(deckContainer, options = {}) {
    this.deck = deckContainer;
    this.threshold = options.threshold || 110;
    this.maxRotation = options.maxRotation || 18;
    this.onSwipe = options.onSwipe || (() => {});
    this.onDragStart = options.onDragStart || (() => {});
    this.onDragEnd = options.onDragEnd || (() => {});

    this.activeCard = null;
    this.nextCard = null;
    this.thirdCard = null;

    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    this.currentDx = 0;
    this.currentDy = 0;
    this.hasCrossedThreshold = false;

    this.bindKeyboard();
  }

  /**
   * Обновление ссылок на карточки в колоде (активная, следующая, третья)
   */
  updateDeckElements() {
    const cards = Array.from(this.deck.querySelectorAll('.vibe-card:not(.fly-right):not(.fly-left)'));
    
    // Очищаем старые классы позиционирования
    cards.forEach(card => {
      card.classList.remove('card-active', 'card-next', 'card-third');
    });

    this.activeCard = cards[0] || null;
    this.nextCard = cards[1] || null;
    this.thirdCard = cards[2] || null;

    if (this.activeCard) {
      this.activeCard.classList.add('card-active');
      this.bindCardEvents(this.activeCard);
    }
    if (this.nextCard) {
      this.nextCard.classList.add('card-next');
    }
    if (this.thirdCard) {
      this.thirdCard.classList.add('card-third');
    }
  }

  /**
   * Привязка событий жестов к активной карточке
   */
  bindCardEvents(card) {
    if (card._hasSwiperAttached) return;
    card._hasSwiperAttached = true;

    card.addEventListener('pointerdown', this.handlePointerDown.bind(this));
    card.addEventListener('pointermove', this.handlePointerMove.bind(this));
    card.addEventListener('pointerup', this.handlePointerUp.bind(this));
    card.addEventListener('pointercancel', this.handlePointerUp.bind(this));
  }

  handlePointerDown(e) {
    if (!this.activeCard || this.isDragging) return;

    // Захватываем указатель для надежности (даже если курсор/палец выйдет за пределы карточки)
    this.activeCard.setPointerCapture(e.pointerId);
    this.activeCard.classList.remove('resetting');

    this.isDragging = true;
    this.startX = e.clientX;
    this.startY = e.clientY;
    this.startTime = performance.now();
    this.currentDx = 0;
    this.currentDy = 0;
    this.hasCrossedThreshold = false;

    this.onDragStart();
  }

  handlePointerMove(e) {
    if (!this.isDragging || !this.activeCard) return;

    this.currentDx = e.clientX - this.startX;
    this.currentDy = e.clientY - this.startY;

    const deckWidth = this.deck.offsetWidth || 340;
    const rotation = (this.currentDx / deckWidth) * this.maxRotation;

    // Перемещение и вращение верхней карточки
    this.activeCard.style.transform = `translate3d(${this.currentDx}px, ${this.currentDy}px, 0) rotate(${rotation}deg)`;

    // Динамическая прозрачность бейджей «🔥 В ПАК» / «❌ СКИП»
    const badgeLike = this.activeCard.querySelector('.badge-like');
    const badgeSkip = this.activeCard.querySelector('.badge-skip');

    if (this.currentDx > 0) {
      const likeOpacity = Math.min(1, this.currentDx / (this.threshold * 0.85));
      if (badgeLike) badgeLike.style.opacity = likeOpacity;
      if (badgeSkip) badgeSkip.style.opacity = 0;
    } else {
      const skipOpacity = Math.min(1, -this.currentDx / (this.threshold * 0.85));
      if (badgeSkip) badgeSkip.style.opacity = skipOpacity;
      if (badgeLike) badgeLike.style.opacity = 0;
    }

    // Тактильный микро-отклик при пересечении порога
    if (Math.abs(this.currentDx) >= this.threshold && !this.hasCrossedThreshold) {
      window.telegramApp?.haptic.selection();
      this.hasCrossedThreshold = true;
    } else if (Math.abs(this.currentDx) < this.threshold && this.hasCrossedThreshold) {
      this.hasCrossedThreshold = false;
    }

    // Плавное приближение следующей карточки в колоде пропорционально прогрессу свайпа
    if (this.nextCard) {
      const progress = Math.min(1, Math.abs(this.currentDx) / (this.threshold * 1.5));
      const nextScale = 0.94 + 0.06 * progress;
      const nextTranslateY = 14 * (1 - progress);
      const nextOpacity = 0.82 + 0.18 * progress;

      this.nextCard.style.transform = `translate3d(0, ${nextTranslateY}px, 0) scale(${nextScale})`;
      this.nextCard.style.opacity = nextOpacity;
    }
  }

  handlePointerUp(e) {
    if (!this.isDragging || !this.activeCard) return;

    this.isDragging = false;
    this.onDragEnd();

    try {
      this.activeCard.releasePointerCapture(e.pointerId);
    } catch (err) {}

    const dt = performance.now() - this.startTime;
    const velocityX = Math.abs(this.currentDx) / (dt || 1);

    // Условие срабатывания свайпа: расстояние больше порога ИЛИ высокая скорость броска
    const isSwiped = Math.abs(this.currentDx) >= this.threshold || velocityX >= 0.65;

    if (isSwiped) {
      const direction = this.currentDx > 0 ? 'right' : 'left';
      this.executeFlyOut(direction);
    } else {
      this.resetActiveCard();
    }
  }

  /**
   * Анимация вылета карточки за экран
   */
  executeFlyOut(direction) {
    if (!this.activeCard) return;

    const cardToFly = this.activeCard;
    const badge = cardToFly.querySelector(direction === 'right' ? '.badge-like' : '.badge-skip');
    if (badge) badge.style.opacity = '1';

    cardToFly.classList.add(direction === 'right' ? 'fly-right' : 'fly-left');
    cardToFly.style.transform = ''; // передаем управление CSS-классу с transition

    // Тактильный фидбек
    if (direction === 'right') {
      window.telegramApp?.haptic.impact('medium');
    } else {
      window.telegramApp?.haptic.impact('light');
    }

    // Оповещаем слушателя
    this.onSwipe(direction, cardToFly);

    // Удаляем карточку из DOM после завершения CSS-анимации
    setTimeout(() => {
      cardToFly.remove();
      this.updateDeckElements();
    }, 320);
  }

  /**
   * Плавный возврат карточки на исходную позицию при неполном жесте
   */
  resetActiveCard() {
    if (!this.activeCard) return;

    this.activeCard.classList.add('resetting');
    this.activeCard.style.transform = '';

    const badgeLike = this.activeCard.querySelector('.badge-like');
    const badgeSkip = this.activeCard.querySelector('.badge-skip');
    if (badgeLike) badgeLike.style.opacity = '0';
    if (badgeSkip) badgeSkip.style.opacity = '0';

    if (this.nextCard) {
      this.nextCard.style.transform = '';
      this.nextCard.style.opacity = '';
    }

    setTimeout(() => {
      if (this.activeCard) {
        this.activeCard.classList.remove('resetting');
      }
    }, 300);
  }

  /**
   * Программный запуск свайпа (для кнопок или горячих клавиш)
   */
  swipeCard(direction) {
    if (!this.activeCard || this.isDragging) return;
    this.executeFlyOut(direction);
  }

  /**
   * Поддержка клавиатуры для удобства на десктопе
   */
  bindKeyboard() {
    window.addEventListener('keydown', (e) => {
      // Игнорируем нажатия, если открыто модальное окно или фокус в инпуте
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        e.preventDefault();
        this.swipeCard('right');
      } else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
        e.preventDefault();
        this.swipeCard('left');
      }
    });
  }
}

window.CardSwiper = CardSwiper;
