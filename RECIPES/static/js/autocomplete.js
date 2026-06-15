// static/js/autocomplete.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("Autocomplete script loaded"); // Проверка загрузки скрипта
   
    // Важно: пути должны точно соответствовать тем, что в Flask
    setupAutocomplete('search_category_input', 'category-results', '/api/search/categories');
    setupAutocomplete('search_object_input', 'object-results', '/api/search/objects');
});

function setupAutocomplete(inputId, resultsId, apiUrl) {
    const input = document.getElementById(inputId);
    const resultsContainer = document.getElementById(resultsId);

    if (!input || !resultsContainer) {
        console.error(`Element not found: ${inputId} or ${resultsId}`);
        return;
    }

    input.addEventListener('input', async () => {
        const query = input.value.trim();
        console.log(`Typing in ${inputId}: "${query}"`); // Логируем ввод

        if (query.length === 0) {
            resultsContainer.innerHTML = '';
            return;
        }

        try {
            // Формируем URL с параметром q
            const url = `${apiUrl}?q=${encodeURIComponent(query)}`;
            console.log(`Fetching from: ${url}`); // Логируем запрос

            const response = await fetch(url);
           
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(`Received data:`, data); // Логируем ответ сервера

            renderResults(data, resultsContainer, apiUrl);
        } catch (error) {
            console.error('Error fetching autocomplete data:', error);
        }
    });

    // Закрытие списка при клике вне его
    document.addEventListener('click', (e) => {
        if (e.target !== input) {
            resultsContainer.innerHTML = '';
        }
    });
}

function renderResults(data, container, apiUrl) {
    container.innerHTML = '';
   
    if (!data || data.length === 0) {
        container.innerHTML = '<div class="dropdown-menu show w-100 p-2 text-muted small">Ничего не найдено</div>';
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'dropdown-menu show w-100 shadow-sm';
    ul.style.maxHeight = '250px';
    ul.style.overflowY = 'auto';
    ul.style.display = 'block'; // Принудительно показываем

    data.forEach(item => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'dropdown-item';
        a.href = '#';
       
        // ОПРЕДЕЛЕНИЕ ТИПА: если в URL есть 'categories', идем в category_page
        const isCategory = apiUrl.includes('categories');
        const url = isCategory
            ? `/category/${item.id}`
            : `/object/${item.id}`;

        a.textContent = item.name;
        a.onclick = (e) => {
            e.preventDefault();
            console.log(`Navigating to: ${url}`);
            window.location.href = url;
        };

        li.appendChild(a);
        ul.appendChild(li);
    });

    container.appendChild(ul);
}
