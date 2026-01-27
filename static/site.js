const BUTTON_BLACKLIST = new Set(['theme-toggle', 'carousel-prev', 'carousel-next']);

const showToast = (message) => {
  window.alert(message);
};

const handleButtonClick = (event) => {
  const button = event.target.closest('button');
  if (!button) return;
  if (BUTTON_BLACKLIST.has(button.id)) return;
  if (button.type === 'submit') return;
  if (button.dataset.link) {
    window.location.href = button.dataset.link;
    return;
  }
  showToast('Demo action: no backend connected.');
};

document.addEventListener('click', handleButtonClick);

document.addEventListener('submit', (event) => {
  event.preventDefault();
  showToast('Form submitted (demo).');
});

const setupTabs = () => {
  const tabs = document.querySelector('[data-tabs]');
  if (!tabs) return;
  const buttons = Array.from(tabs.querySelectorAll('button[data-tab-target]'));
  const panels = Array.from(document.querySelectorAll('[data-tab-panel]'));

  const setActive = (target) => {
    buttons.forEach((btn) => {
      const isActive = btn.dataset.tabTarget === target;
      btn.classList.toggle('text-[var(--text-main)]', isActive);
      btn.classList.toggle('font-bold', isActive);
      btn.classList.toggle('border-yellow-400', isActive);
      btn.classList.toggle('border-transparent', !isActive);
      btn.classList.toggle('text-[var(--text-muted)]', !isActive);
    });
    panels.forEach((panel) => {
      panel.classList.toggle('hidden', panel.dataset.tabPanel !== target);
    });
  };

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => setActive(btn.dataset.tabTarget));
  });
};

const setupCatalogFilters = () => {
  const search = document.getElementById('catalog-search');
  const category = document.getElementById('catalog-category');
  const sort = document.getElementById('catalog-sort');
  const cards = Array.from(document.querySelectorAll('[data-category]'));
  if (!search || !category || !sort || cards.length === 0) return;

  const applyFilters = () => {
    const query = search.value.trim().toLowerCase();
    const selectedCategory = category.value;

    cards.forEach((card) => {
      const title = card.querySelector('h3')?.textContent?.toLowerCase() || '';
      const matchesQuery = title.includes(query);
      const matchesCategory = selectedCategory === 'All Categories' || card.dataset.category === selectedCategory;
      card.classList.toggle('hidden', !(matchesQuery && matchesCategory));
    });
  };

  const applySort = () => {
    const grid = cards[0].parentElement;
    if (!grid) return;
    const visibleCards = cards.filter((card) => !card.classList.contains('hidden'));
    const sortValue = sort.value;

    const sorted = visibleCards.slice().sort((a, b) => {
      if (sortValue === 'Price: Low to High') {
        return Number(a.dataset.price) - Number(b.dataset.price);
      }
      if (sortValue === 'Price: High to Low') {
        return Number(b.dataset.price) - Number(a.dataset.price);
      }
      if (sortValue === 'Popular') {
        return Number(b.dataset.popularity) - Number(a.dataset.popularity);
      }
      if (sortValue === 'Newest') {
        return Number(a.dataset.order) - Number(b.dataset.order);
      }
      return 0;
    });

    sorted.forEach((card) => grid.appendChild(card));
  };

  search.addEventListener('input', () => {
    applyFilters();
    applySort();
  });
  category.addEventListener('change', () => {
    applyFilters();
    applySort();
  });
  sort.addEventListener('change', applySort);

  applyFilters();
  applySort();
};

document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupCatalogFilters();
});
