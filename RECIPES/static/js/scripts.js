// ✅ Функция добавления новой строки ингредиента
function addIngredientRow() {
  const container = document.getElementById('ingredients-container');
  const newRow = document.createElement('div');
  newRow.className = 'ingredient-row mb-3 d-flex gap-2';
  newRow.innerHTML = `
    <input type="text" name="ingredient_name[]" class="form-control" placeholder="Название" required>
    <input type="number" name="ingredient_amount[]" class="form-control" placeholder="Кол-во" min="0" step="any" style="width: 80px;">
    <select name="ingredient_unit[]" class="form-select" required style="width: 60px;">
      <option value="ml">мл</option>
      <option value="g">г</option>
      <option value="pc">шт</option>
    </select>
    <button type="button" class="btn btn-outline-danger" onclick="this.closest('.ingredient-row').remove()">🗑️</button>
  `;
  container.appendChild(newRow);
}

// ✅ Инициализация: добавляем обработчик на все кнопки "+ Добавить"
document.addEventListener('DOMContentLoaded', function() {
  // Обработчик для существующих кнопок
  document.querySelectorAll('button.btn-secondary.btn-sm').forEach(button => {
    if (button.textContent.includes('Добавить')) {
      button.addEventListener('click', addIngredientRow);
    }
  });

  // Обработчик для динамически добавленных элементов
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === 1) { // элемент
          if (node.classList && node.classList.contains('btn-secondary') && node.textContent.includes('Добавить')) {
            node.addEventListener('click', addIngredientRow);
          }
        }
      });
    });
  });
  const container = document.getElementById('ingredients-container');
  if (container) {
    observer.observe(container, { childList: true, subtree: true });
  }
});