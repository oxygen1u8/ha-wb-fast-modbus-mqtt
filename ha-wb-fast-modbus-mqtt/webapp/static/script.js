// Функция загрузки портов
async function loadPorts() {
    try {
        console.log('Loading ports from /ports endpoint...');
        const response = await fetch('./ports');
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Received data:', data);
        
        if (data.error) {
            console.error('Error loading ports:', data.error);
            // В случае ошибки оставляем пустой список
            const portSelect = document.getElementById('portSelect');
            portSelect.innerHTML = '<option value="" class="bg-gray-700">Выберите порт</option>';
            portSelect.disabled = true;
            // Показываем сообщение об ошибке
            const errorDiv = document.createElement('div');
            errorDiv.className = 'text-red-400 text-sm mt-2';
            errorDiv.textContent = 'Не удалось загрузить список портов';
            portSelect.parentNode.appendChild(errorDiv);
        } else {
            const portSelect = document.getElementById('portSelect');
            portSelect.innerHTML = '<option value="" class="bg-gray-700">Выберите порт</option>';
            
            // Проверяем, есть ли порты в ответе
            if (data.ports && Array.isArray(data.ports) && data.ports.length > 0) {
                console.log('Found ports:', data.ports);
                data.ports.forEach(port => {
                    // Проверяем, что порт не пустой
                    if (port && typeof port === 'string' && port.trim() !== "") {
                        portSelect.innerHTML += `<option value="${port}" class="bg-gray-700">${port}</option>`;
                    }
                });
                portSelect.disabled = false;
            } else {
                // Если порты отсутствуют, показываем сообщение
                console.log('No ports found');
                portSelect.innerHTML += '<option value="" class="bg-gray-700" disabled>Порты не найдены</option>';
                portSelect.disabled = true;
            }
        }
        
        // Включаем кнопку при выборе порта
        const portSelect = document.getElementById('portSelect');
        portSelect.addEventListener('change', function() {
            const button = document.getElementById('scanButton');
            if (this.value) {
                button.disabled = false;
            } else {
                button.disabled = true;
            }
        });
    } catch (error) {
        console.error('Error loading ports:', error);
        // В случае ошибки оставляем пустой список
        const portSelect = document.getElementById('portSelect');
        portSelect.innerHTML = '<option value="" class="bg-gray-700">Выберите порт</option>';
        portSelect.disabled = true;
        // Показываем сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-red-400 text-sm mt-2';
        errorDiv.textContent = 'Не удалось загрузить список портов';
        portSelect.parentNode.appendChild(errorDiv);
    }
}

// Функция для запуска сканирования с выбранным портом
function startScan() {
    const button = document.getElementById('scanButton');
    const status = document.getElementById('scanStatus');
    const portSelect = document.getElementById('portSelect');
    const selectedPort = portSelect.value;
    
    if (!selectedPort) {
        alert('Пожалуйста, выберите порт для сканирования');
        return;
    }
    
    // Отключаем кнопку и показываем статус
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Сканирование...';
    status.classList.remove('hidden');
    
    // Выполняем POST запрос к API с указанием порта
    fetch('/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            port: selectedPort
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Scan started:', data);
        // Обновляем логи через 1 секунду
        setTimeout(updateLogs, 1000);
        // После завершения сканирования возвращаем кнопку в исходное состояние
        setTimeout(() => {
            status.classList.add('hidden');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search mr-2"></i> Сканировать';
        }, 8000); // Возвращаем через 8 секунд для лучшего UX
    })
    .catch(error => {
        console.error('Error:', error);
        status.classList.add('hidden');
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-search mr-2"></i> Сканировать';
        alert('Ошибка запуска сканирования: ' + error.message);
    });
}

// Функция для обновления логов
function updateLogs() {
    fetch('/logs')
    .then(response => response.json())
    .then(data => {
        const logsContent = document.getElementById('logsContent');
        
        if (data.logs.length === 0) {
            logsContent.innerHTML = '<p class="text-gray-500 italic">Логи сканирования будут отображаться здесь...</p>';
        } else {
            // Создаем HTML содержимое с правильным форматированием
            let logsHtml = '';
            data.logs.forEach(log => {
                // Заменяем переносы строк на <br> теги для отображения в HTML
                const formattedLog = log.replace(/\n/g, '<br>');
                logsHtml += `<div class="log-entry py-1 border-b border-gray-700">${formattedLog}</div>`;
            });
            logsContent.innerHTML = logsHtml;
        }
        
        // Прокручиваем вниз
        logsContent.scrollTop = logsContent.scrollHeight;
    })
    .catch(error => {
        console.error('Error fetching logs:', error);
    });
}

// Функция для очистки логов
function clearLogs() {
    const logsContent = document.getElementById('logsContent');
    logsContent.innerHTML = '<p class="text-gray-500 italic">Логи сканирования будут отображаться здесь...</p>';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    updateLogs();
    loadPorts();
});

// Обновляем логи каждые 2 секунды
setInterval(updateLogs, 2000);