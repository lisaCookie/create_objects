
  function addIngredientRow() {
    const container = document.getElementById('ingredients-container');
    const newRow = document.createElement('div');
    newRow.className = 'ingredient-row mb-3 d-flex gap-2';
    newRow.innerHTML = `
      <input type="text" name="ingredient_name[]" class="form-control" placeholder="Название" required>
      <input type="number" name="ingredient_amount[]" class="form-control" placeholder="Кол-во" min="0" required style="width: 80px;">
      <select name="ingredient_unit[]" class="form-select" required style="width: 60px;">
        <option value="ml">мл</option>
        <option value="g">г</option>
        <option value="pc">шт</option>
      </select>
      <button type="button" class="btn btn-outline-danger" onclick="this.closest('.ingredient-row').remove()">🗑️</button>
    `;
    container.appendChild(newRow);
  }

  // ✅ Инициализация: добавляем обработчик на ВСЕ кнопки "+ Добавить"
  document.addEventListener('DOMContentLoaded', function() {
    // Привязываем обработчик к КАЖДОЙ кнопке "+ Добавить" — даже если они появились при редактировании
    document.querySelectorAll('button.btn-secondary.btn-sm').forEach(button => {
      if (button.textContent.includes('Добавить')) {
        button.addEventListener('click', addIngredientRow);
      }
    });

    // ✅ Дополнительно: если кнопка была добавлена динамически — тоже обрабатываем
    // (на всякий случай — если вы потом добавите кнопки через JS)
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (node.nodeType === 1) { // Элемент
            if (node.classList && node.classList.contains('btn-secondary') && node.textContent.includes('Добавить')) {
              node.addEventListener('click', addIngredientRow);
            }
          }
        });
      });
    });

    observer.observe(document.getElementById('ingredients-container'), { childList: true, subtree: true });
  });