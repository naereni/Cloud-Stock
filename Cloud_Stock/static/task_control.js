document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggle-push-stocks');
    let isTaskEnabled = true;

    // Add initial classes
    toggleButton.classList.add('task-control-btn');
    toggleButton.classList.add('enabled');

    toggleButton.addEventListener('click', function() {
        fetch('/api/toggle-push-stocks/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrf-token]').content,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            isTaskEnabled = data.is_enabled;
            toggleButton.textContent = isTaskEnabled ? 'Отключить Push-Stocks' : 'Включить Push-Stocks';
            toggleButton.classList.toggle('enabled', isTaskEnabled);
            toggleButton.classList.toggle('disabled', !isTaskEnabled);
        })
        .catch(error => console.error('Error:', error));
    });
});

// Add styles
const style = document.createElement('style');
style.textContent = `
    .task-control-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .task-control-btn.enabled {
        background-color: #4CAF50;
        color: white;
    }

    .task-control-btn.disabled {
        background-color: #f44336;
        color: white;
    }

    .task-control-btn:hover {
        opacity: 0.9;
    }
`;
document.head.appendChild(style);