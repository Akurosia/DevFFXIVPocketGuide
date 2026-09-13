(function () {
  function normalize(value) {
    return (value || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function escapeForSelector(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
    return (value || "").replace(/([ #;?%&,.+*~\':"!^$\[\]()=>|\/@])/g, "\\$1");
  }

  function sortCards(container, value) {
    const cards = Array.from(container.querySelectorAll('[data-achievement-card]'));
    const compare = {
      'order-asc': (a, b) => (+a.dataset.achievementOrder || 0) - (+b.dataset.achievementOrder || 0),
      'name-asc': (a, b) => (a.dataset.achievementName || '').localeCompare((b.dataset.achievementName || ''), undefined, { sensitivity: 'base' }),
      'points-desc': (a, b) => (+b.dataset.achievementPoints || 0) - (+a.dataset.achievementPoints || 0),
      'points-asc': (a, b) => (+a.dataset.achievementPoints || 0) - (+b.dataset.achievementPoints || 0),
    }[value] || ((a, b) => (+a.dataset.achievementOrder || 0) - (+b.dataset.achievementOrder || 0));

    cards.sort(compare).forEach((card) => container.appendChild(card));
  }

  function initAchievements() {
    const shell = document.querySelector('.achievement-browser');
    if (!shell) return;

    const cards = Array.from(shell.querySelectorAll('[data-achievement-card]'));
    const sections = Array.from(shell.querySelectorAll('[data-achievement-section]'));
    const navLinks = Array.from(shell.querySelectorAll('[data-achievement-nav]'));

    const searchInput = document.getElementById('achievementSearch');
    const sortSelect = document.getElementById('achievementSort');
    const hasItem = document.getElementById('achievementHasItem');
    const hasTitle = document.getElementById('achievementHasTitle');
    const resetButton = document.getElementById('achievementReset');
    const visibleCount = shell.querySelector('[data-achievement-visible]');
    const totalCount = shell.querySelector('[data-achievement-total]');
    const sidebarTotalCount = shell.querySelector('[data-achievement-count-total]');
    const contextText = shell.querySelector('[data-achievement-context]');
    const emptyState = shell.querySelector('.achievement-empty');

    const state = {
      main: '',
      sub: '',
      search: '',
      hasItem: false,
      hasTitle: false,
      sort: sortSelect ? sortSelect.value : 'order-asc',
    };

    const total = cards.length;
    if (visibleCount) visibleCount.textContent = String(total);
    if (totalCount) totalCount.textContent = String(total);
    if (sidebarTotalCount) sidebarTotalCount.textContent = String(total);

    sections.forEach((section) => {
      const grid = section.querySelector('.achievement-section__grid');
      if (grid) sortCards(grid, state.sort);
    });

    function applyFilters(scrollTargetId) {
      let visible = 0;

      sections.forEach((section) => {
        const grid = section.querySelector('.achievement-section__grid');
        if (grid) sortCards(grid, state.sort);
      });

      cards.forEach((card) => {
        const cardMain = card.dataset.achievementMain || '';
        const cardSub = card.dataset.achievementSub || '';
        const cardSearch = normalize(card.dataset.achievementSearch || '');
        const matchMain = !state.main || cardMain === state.main;
        const matchSub = !state.sub || cardSub === state.sub;
        const matchSearch = !state.search || cardSearch.includes(state.search);
        const matchItem = !state.hasItem || card.dataset.achievementHasItem === 'true';
        const matchTitle = !state.hasTitle || card.dataset.achievementHasTitle === 'true';
        const visibleNow = matchMain && matchSub && matchSearch && matchItem && matchTitle;
        card.hidden = !visibleNow;
        if (visibleNow) visible += 1;
      });

      sections.forEach((section) => {
        const allCards = Array.from(section.querySelectorAll('[data-achievement-card]'));
        const visibleCards = allCards.filter((card) => !card.hidden);
        section.hidden = visibleCards.length === 0;
        const badge = section.querySelector('[data-achievement-section-visible]');
        if (badge) badge.textContent = String(visibleCards.length);
      });

      if (visibleCount) visibleCount.textContent = String(visible);
      if (emptyState) emptyState.hidden = visible !== 0;

      const contextParts = [];
      if (state.main) contextParts.push(state.main);
      if (state.sub) contextParts.push(state.sub);
      if (state.search) contextParts.push('Suche: "' + searchInput.value.trim() + '"');
      if (state.hasItem) contextParts.push('mit Item');
      if (state.hasTitle) contextParts.push('mit Titel');
      if (contextText) contextText.textContent = contextParts.length ? contextParts.join(' · ') : 'Alle Kategorien';

      navLinks.forEach((link) => {
        const isActive = (link.dataset.filterMain || '') === state.main && (link.dataset.filterSub || '') === state.sub;
        link.classList.toggle('is-active', isActive);
      });

      if (scrollTargetId) {
        if (scrollTargetId === 'all') {
          shell.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          const target = document.getElementById(scrollTargetId);
          if (target && !target.hidden) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }

    navLinks.forEach((link) => {
      link.addEventListener('click', () => {
        state.main = link.dataset.filterMain || '';
        state.sub = link.dataset.filterSub || '';
        applyFilters(link.dataset.targetSection || 'all');
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        state.search = normalize(searchInput.value);
        applyFilters();
      });
    }

    if (sortSelect) {
      sortSelect.addEventListener('change', () => {
        state.sort = sortSelect.value;
        applyFilters();
      });
    }

    if (hasItem) {
      hasItem.addEventListener('change', () => {
        state.hasItem = !!hasItem.checked;
        applyFilters();
      });
    }

    if (hasTitle) {
      hasTitle.addEventListener('change', () => {
        state.hasTitle = !!hasTitle.checked;
        applyFilters();
      });
    }

    if (resetButton) {
      resetButton.addEventListener('click', () => {
        state.main = '';
        state.sub = '';
        state.search = '';
        state.hasItem = false;
        state.hasTitle = false;
        state.sort = 'order-asc';
        if (searchInput) searchInput.value = '';
        if (sortSelect) sortSelect.value = state.sort;
        if (hasItem) hasItem.checked = false;
        if (hasTitle) hasTitle.checked = false;
        applyFilters('all');
      });
    }

    // Deep-link support: #section-kampferfolge etc.
    const hash = window.location.hash.replace('#', '');
    if (hash) {
      const directLink = shell.querySelector('[data-target-section="' + escapeForSelector(hash) + '"]');
      if (directLink) directLink.click();
    }

    applyFilters();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAchievements);
  } else {
    initAchievements();
  }
})();
