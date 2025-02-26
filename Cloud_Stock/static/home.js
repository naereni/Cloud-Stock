   // home.js

   // Function to retrieve CSRF token from meta tag
   function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// Function to apply changes in cells
function applyChanges(inputElement, valueElement) {
    valueElement.textContent = inputElement.value;
    valueElement.style.display = 'inline';
    inputElement.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = getCsrfToken();

    // Кнопка для пулла остатков с озона с подтверждением
    const pullOzonButton = document.getElementById('pull-ozon-button');
    if (pullOzonButton) {
        pullOzonButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default form submission
            if (confirm('Вы уверены, что хотите вытянуть остатки с Озона?')) {
                fetch("/pull_ozon_stocks/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({})
                })
                .then(response => {
                    if (response.ok) {
                        console.log("Запрос отправлен");
                        // Optionally, redirect or update the UI
                        window.location.href = "{% url 'success_pull' %}";
                    } else {
                        console.error('Ошибка при отправке запроса:', response.statusText);
                    }
                })
                .catch(error => {
                    console.error('Ошибка при отправке запроса:', error);
                });
            }
        });
    }

    // Поиск по названию (Real-time search)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            const searchValue = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#dynamic-table tbody tr');
            rows.forEach(function (row) {
                const titleCell = row.querySelector('td');
                if (titleCell) {
                    const title = titleCell.textContent.toLowerCase();
                    row.style.display = title.includes(searchValue) ? '' : 'none';
                }
            });
        });
    }

    // Автоматическая фильтрация при выборе города
    const citySelect = document.getElementById('city');
    const filterForm = document.getElementById('filter-form');
    if (citySelect && filterForm) {
        citySelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }

    // Редактирование остатка и авито
    const stockCells = document.querySelectorAll('.total_stock-cell');
    const avitoCells = document.querySelectorAll('.avito-cell');

    stockCells.forEach(cell => {
        const stockValue = cell.querySelector('.total_stock-value');
        const stockInput = cell.querySelector('.total_stock-input');

        cell.addEventListener('click', function() {
            stockValue.style.display = 'none';
            stockInput.style.display = 'inline';
            stockInput.focus();
        });

        stockInput.addEventListener('blur', function() {
            applyChanges(stockInput, stockValue);
        });

        stockInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                applyChanges(stockInput, stockValue);
                document.getElementById('batch-edit-form').submit();
            }
        });
    });

    avitoCells.forEach(cell => {
        const avitoValue = cell.querySelector('.avito-value');
        const avitoInput = cell.querySelector('.avito-input');

        cell.addEventListener('click', function() {
            avitoValue.style.display = 'none';
            avitoInput.style.display = 'inline';
            avitoInput.focus();
        });

        avitoInput.addEventListener('blur', function() {
            applyChanges(avitoInput, avitoValue);
        });

        avitoInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                applyChanges(avitoInput, avitoValue);
                document.getElementById('batch-edit-form').submit();
            }
        });
    });

    // Обработчик для кнопки "save-changes"
    const saveChangesButton = document.getElementById('save-changes');
    if (saveChangesButton) {
        saveChangesButton.addEventListener('click', function () {
            console.log("Save button clicked");
            const form = document.getElementById('batch-edit-form');
            console.log("Form data before submit:", new FormData(form));
            form.submit();
        });
    }
});