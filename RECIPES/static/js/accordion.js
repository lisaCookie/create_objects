// RECIPES/static/js/accordion.js

document.addEventListener('DOMContentLoaded', function() {
  // Найти все карточки с классом 'accordion-item'
  const accordionItems = document.querySelectorAll('.accordion-item');

  accordionItems.forEach(item => {
    const header = item.querySelector('.card-header');
    const body = item.querySelector('.card-body');
    const icon = item.querySelector('.expand-icon');

    // Клик по заголовку
    header.addEventListener('click', function() {
      item.classList.toggle('active');
      // Раскрытие/сворачивание содержимого
      if (item.classList.contains('active')) {
        body.style.display = 'block';
      } else {
        body.style.display = 'none';
      }
    });

    // Изначально скрыть содержимое (кроме заголовка)
    body.style.display = 'none';
    header.style.cursor = 'pointer';
    icon.classList.add('collapsed-icon');
  });
});
