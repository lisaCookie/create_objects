// moveObject.js — вынесена вся логика перемещения объектов

export function debounce(func, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

export async function setupMoveObjectLogic() {
  const searchObjectInput = document.getElementById('search_object_input');
  const searchCategoryInput = document.getElementById('search_category_input');
  const objectSuggestions = document.getElementById('object_suggestions');
  const categorySuggestions = document.getElementById('category_suggestions');
  const selectedObjectId = document.getElementById('selected_object_id');
  const selectedCategoryId = document.getElementById('selected_category_id');
  const moveBtn = document.getElementById('move_object_btn');
  const moveResult = document.getElementById('move_result');

  // Поиск объектов
  searchObjectInput.addEventListener('input', debounce(async () => {
    const q = searchObjectInput.value.trim();
    if (q.length < 2) {
      objectSuggestions.style.display = 'none';
      selectedObjectId.value = '';
      return;
    }
    const res = await fetch(`/admin/ajax/search_objects?q=${encodeURIComponent(q)}`);
    const items = await res.json();
    objectSuggestions.innerHTML = '';
    if (items.length === 0) {
      objectSuggestions.style.display = 'none';
      return;
    }
    items.forEach(item => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center';
      li.innerHTML = `${item.name} <small class="text-muted">(${item.category_name})</small>`;
      li.onclick = () => {
        searchObjectInput.value = item.name;
        selectedObjectId.value = item.id;
        objectSuggestions.style.display = 'none';
      };
      objectSuggestions.appendChild(li);
    });
    objectSuggestions.style.display = 'block';
  }, 300));

  // Поиск категорий
  searchCategoryInput.addEventListener('input', debounce(async () => {
    const q = searchCategoryInput.value.trim();
    if (q.length < 1) {
      categorySuggestions.style.display = 'none';
      selectedCategoryId.value = '';
      return;
    }
    const res = await fetch(`/admin/ajax/search_categories?q=${encodeURIComponent(q)}`);
    const items = await res.json();
    categorySuggestions.innerHTML = '';
    if (items.length === 0) {
      categorySuggestions.style.display = 'none';
      return;
    }
    items.forEach(item => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.textContent = item.name;
      li.onclick = () => {
        searchCategoryInput.value = item.name;
        selectedCategoryId.value = item.id;
        categorySuggestions.style.display = 'none';
      };
      categorySuggestions.appendChild(li);
    });
    categorySuggestions.style.display = 'block';
  }, 300));

  // Кнопка "Переместить"
  moveBtn.addEventListener('click', async () => {
    const objId = selectedObjectId.value;
    const catId = selectedCategoryId.value;
    if (!objId || !catId) {
      moveResult.innerHTML = '<div class="alert alert-warning">Выберите объект и категорию.</div>';
      return;
    }
    moveBtn.disabled = true;
    moveResult.innerHTML = '<div class="alert alert-info">Перемещение...</div>';
    const res = await fetch('/admin/move_object', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `object_id=${objId}&new_category_id=${catId}`
    });
    const data = await res.json();
    moveBtn.disabled = false;
    if (data.success) {
      moveResult.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
      // Очистка полей
      searchObjectInput.value = '';
      searchCategoryInput.value = '';
      selectedObjectId.value = '';
      selectedCategoryId.value = '';
      objectSuggestions.style.display = 'none';
      categorySuggestions.style.display = 'none';
    } else {
      moveResult.innerHTML = `<div class="alert alert-danger">${data.error || 'Ошибка перемещения.'}</div>`;
    }
  });
}
