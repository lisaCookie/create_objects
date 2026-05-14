// dashboard.js — инициализация DOM и вызов модулей

import { setupMoveObjectLogic } from './moveObject.js';

document.addEventListener('DOMContentLoaded', () => {
  setupMoveObjectLogic();
});

// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
  const filterCreator = document.getElementById('filter_creator');
  const filterCategory = document.getElementById('filter_category');
  const filterObject = document.getElementById('filter_object');
  const clearFiltersBtn = document.getElementById('clear_filters');

  // Обновить URL и перезагрузить страницу с текущими фильтрами
  function applyFilters() {
    const params = new URLSearchParams();
    if (filterCreator.value) params.append('creator_id', filterCreator.value);
    if (filterCategory.value) params.append('category_id', filterCategory.value);
    if (filterObject.value) params.append('object_id', filterObject.value);

    const url = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.location.href = url;
  }

  // Слушаем изменения в каждом фильтре
  [filterCreator, filterCategory, filterObject].forEach(select => {
    select.addEventListener('change', applyFilters);
  });

  // Слушаем кнопку "Очистить фильтры"
  clearFiltersBtn.addEventListener('click', () => {
    // Сбрасываем все select
    filterCreator.value = '';
    filterCategory.value = '';
    filterObject.value = '';
    // Перезагружаем без параметров
    window.location.href = window.location.pathname;
  });
});