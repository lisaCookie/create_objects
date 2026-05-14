// RECIPES/static/js/sitemap_lazy.js

// Функция для генерации URL в JS (аналог url_for)
function url_for(endpoint, params = {}) {
  const base = window.location.origin;
  if (endpoint === 'objects.category_page') {
    if (params.category_id !== undefined && params.category_id !== null && typeof params.category_id === 'number') {
      return `${base}/category/${params.category_id}`;
    }
    return '#';
  }
  if (endpoint === 'objects.object_detail') {
    if (params.object_id !== undefined && params.object_id !== null && typeof params.object_id === 'number') {
      return `${base}/object/${params.object_id}`;
    }
    return '#';
  }
  return '#'; // По умолчанию
}

// Функция для рекурсивной отрисовки узла
function renderNode(container, nodeData, isRoot = false) {
  if (!nodeData) return;
  const nodeId = nodeData.id;
  const nodeName = nodeData.name;
  const nodeType = nodeData.type; // 'category' or 'object'

  if (nodeType === 'category') {
    const categoryNodeDiv = document.createElement('div');
    categoryNodeDiv.className = 'sitemap-node';
    categoryNodeDiv.id = `node-${nodeId}`;

    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'sitemap-category';
    categoryDiv.dataset.categoryId = nodeId;

    const toggleIcon = document.createElement('span');
    toggleIcon.className = 'toggle-icon';
    toggleIcon.textContent = '▶';

    const categoryLink = document.createElement('a');
    categoryLink.href = url_for('objects.category_page', { category_id: nodeId });
    categoryLink.textContent = nodeName;

    categoryDiv.appendChild(toggleIcon);
    categoryDiv.appendChild(categoryLink);
    categoryNodeDiv.appendChild(categoryDiv);

    const childrenContainer = document.createElement('div');
    childrenContainer.className = 'sitemap-children';
    childrenContainer.id = `children-${nodeId}`;
    childrenContainer.dataset.parentId = nodeId;
    categoryNodeDiv.appendChild(childrenContainer);

    container.appendChild(categoryNodeDiv);

    // Обработчик клика
    categoryDiv.addEventListener('click', function(e) {
      if (e.target.tagName === 'A') return;
      e.preventDefault();

      const isExpanded = this.classList.contains('expanded');
      const icon = this.querySelector('.toggle-icon');
      const childrenContainer = this.nextElementSibling;

      if (isExpanded) {
        childrenContainer.classList.remove('loaded');
        childrenContainer.innerHTML = '';
        icon.textContent = '▶';
        this.classList.remove('expanded');
      } else {
        icon.textContent = '⏳';
        this.classList.add('expanded');

        fetch(`/sitemap/children/${nodeId}`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
          })
          .then(data => {
            childrenContainer.innerHTML = '';
            if (data.children && data.children.length > 0) {
              data.children.forEach(child => renderNode(childrenContainer, { ...child, type: 'category' }));
            }
            if (data.objects && data.objects.length > 0) {
              data.objects.forEach(obj => renderNode(childrenContainer, { ...obj, type: 'object' }));
            }
            if ((!data.children || data.children.length === 0) && (!data.objects || data.objects.length === 0)) {
              childrenContainer.innerHTML = '<div class="text-muted small">Нет подкатегорий или рецептов.</div>';
              childrenContainer.classList.add('loaded');
              icon.textContent = '►';
            } else {
              childrenContainer.classList.add('loaded');
              icon.textContent = '▼';
            }
          })
          .catch(error => {
            console.error('Error fetching children:', error);
            childrenContainer.innerHTML = '<div class="text-danger small">Ошибка загрузки.</div>';
            icon.textContent = '❌';
            this.classList.remove('expanded');
          });
      }
    });
  } else if (nodeType === 'object') {
    const objectDiv = document.createElement('div');
    objectDiv.className = 'sitemap-object';

    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = '📄';

    const objectLink = document.createElement('a');
    objectLink.href = url_for('objects.object_detail', { object_id: nodeId });
    objectLink.textContent = nodeName;

    objectDiv.appendChild(icon);
    objectDiv.appendChild(objectLink);
    container.appendChild(objectDiv);
  }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
  const sitemapRoot = document.getElementById('sitemap-root');

  // Обработка уже отрисованных корневых категорий
  document.querySelectorAll('#sitemap-root .sitemap-node').forEach(nodeEl => {
    const categoryDiv = nodeEl.querySelector('.sitemap-category');
    const categoryId = categoryDiv.dataset.categoryId;
    const childrenContainer = nodeEl.querySelector('.sitemap-children');
    const toggleIcon = categoryDiv.querySelector('.toggle-icon');

    categoryDiv.addEventListener('click', function(e) {
      if (e.target.tagName === 'A') return;
      e.preventDefault();

      const isExpanded = this.classList.contains('expanded');
      const icon = this.querySelector('.toggle-icon');
      const childrenContainer = this.nextElementSibling;

      if (isExpanded) {
        childrenContainer.classList.remove('loaded');
        childrenContainer.innerHTML = '';
        icon.textContent = '▶';
        this.classList.remove('expanded');
      } else {
        icon.textContent = '⏳';
        this.classList.add('expanded');

        fetch(`/sitemap/children/${categoryId}`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
          })
          .then(data => {
            childrenContainer.innerHTML = '';
            if (data.children && data.children.length > 0) {
              data.children.forEach(child => renderNode(childrenContainer, { ...child, type: 'category' }));
            }
            if (data.objects && data.objects.length > 0) {
              data.objects.forEach(obj => renderNode(childrenContainer, { ...obj, type: 'object' }));
            }
            if ((!data.children || data.children.length === 0) && (!data.objects || data.objects.length === 0)) {
              childrenContainer.innerHTML = '<div class="text-muted small">Нет подкатегорий или рецептов.</div>';
              childrenContainer.classList.add('loaded');
              icon.textContent = '►';
            } else {
              childrenContainer.classList.add('loaded');
              icon.textContent = '▼';
            }
          })
          .catch(error => {
            console.error('Error fetching children:', error);
            childrenContainer.innerHTML = '<div class="text-danger small">Ошибка загрузки.</div>';
            icon.textContent = '❌';
            this.classList.remove('expanded');
          });
      }
    });
  });
});