tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#137fec",
                "background-light": "#f6f7f8",
                "background-dark": "#0f1115",
                "card-dark": "#1a1d23",
                "border-dark": "#2d343d"
            },
            fontFamily: {
                "display": ["Space Grotesk", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
            },
        },
    },
};

// Функция для получения списка портов
async function loadSerialPorts() {
    try {
        const response = await fetch('./ports');
        if (response.ok) {
            const data = await response.json();
            const portSelect = document.getElementById('port-select');
            
            if (portSelect) {
                // Очищаем существующие опции
                portSelect.innerHTML = '';

                // Добавляем новые опции
                data.port_list.forEach(port => {
                    const option = document.createElement('option');
                    option.value = port;
                    option.textContent = port;
                    portSelect.appendChild(option);
                });
            }
        } else {
            console.error('Ошибка получения списка портов:', response.status);
        }
    } catch (error) {
        console.error('Ошибка сети при получении портов:', error);
    }
}

// Функция для обновления таблицы устройств
function updateDevicesTable(devices) {
    const tableBody = document.getElementById('devices-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-slate-50 dark:hover:bg-border-dark/20 transition-colors';
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <div class="text-sm font-bold text-slate-900 dark:text-white">${device.slave_name || 'Неизвестно'}</div>
            </td>
            <td class="px-6 py-4 text-sm font-mono text-slate-600 dark:text-slate-400">0x${device.slave_id.toString(16).toUpperCase()} (${device.slave_id})</td>
            <td class="px-6 py-4 text-sm font-mono text-slate-600 dark:text-slate-400">
                0x${device.serial_num.toString(16).toUpperCase().padStart(8, '0')}
            </td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">${device.baudrate || 'Нет данных'}</td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">${device.parity || 'Нет данных'}</td>
            <td class="px-6 py-4 text-right">
                <button class="p-2 hover:bg-slate-200 dark:hover:bg-border-dark rounded transition-colors text-slate-400">
                    <span class="material-symbols-outlined text-xl">tune</span>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Настройка кнопки сканирования устройств
function setupDeviceScanButton() {
    // Находим кнопку сканирования по тексту
    const scanButtons = document.querySelectorAll('button');
    let scanButton = null;

    scanButtons.forEach(button => {
        if (button.textContent.includes('Сканировать')) {
            scanButton = button;
        }
    });

    if (scanButton) {
        scanButton.addEventListener('click', async () => {
            try {
                // Добавляем анимацию к кнопке
                const syncIcon = scanButton.querySelector('.material-symbols-outlined');
                if (syncIcon) {
                    syncIcon.classList.add('sync-animation');
                }

                // Получаем выбранный порт
                const portSelect = document.getElementById('port-select');
                const selectedPort = portSelect ? portSelect.value : "/dev/ttyUSB0";

                // Собираем выбранные скорости
                // Ищем все чекбоксы с атрибутом value (это чекбоксы скоростей)
                const baudrateCheckboxes = document.querySelectorAll('input[type="checkbox"][value]');
                const selectedBaudrates = [];
                baudrateCheckboxes.forEach(cb => {
                    // Проверяем, отмечен ли чекбокс (через свойство checked)
                    if (cb.checked) {
                        selectedBaudrates.push(parseInt(cb.value));
                    }
                });

                // Собираем выбранные типы четности
                const selectedParities = [];
                
                // Находим чекбоксы четности по их тексту
                const parityLabels = document.querySelectorAll('label.flex.items-center.gap-3.cursor-pointer.group');
                parityLabels.forEach(label => {
                    const span = label.querySelector('span');
                    if (span) {
                        const text = span.textContent;
                        // Проверяем, отмечен ли чекбокс внутри этой метки
                        const checkbox = label.querySelector('input[type="checkbox"]');
                        if (checkbox && checkbox.checked) {
                            if (text.includes('Нет')) {
                                selectedParities.push('N');
                            } else if (text.includes('Чет')) {
                                selectedParities.push('E');
                            } else if (text.includes('Нечет')) {
                                selectedParities.push('O');
                            }
                        }
                    }
                });

                // Отправляем POST запрос на /scan endpoint
                const response = await fetch('./scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        "port": selectedPort,
                        "baudrate": selectedBaudrates,
                        "parity": selectedParities
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log('Scan result:', result);
                    
                    // Обновляем таблицу устройств
                    if (result.slave_list) {
                        updateDevicesTable(result.slave_list);
                    }
                    
                    alert('Сканирование завершено');
                } else {
                    console.error('Ошибка сканирования:', response.status);
                    alert('Ошибка при сканировании');
                }
            } catch (error) {
                console.error('Ошибка сети:', error);
                alert('Ошибка сети при сканировании');
            } finally {
                // Убираем анимацию после завершения запроса
                const syncIcon = scanButton.querySelector('.material-symbols-outlined');
                if (syncIcon) {
                    syncIcon.classList.remove('sync-animation');
                }
            }
        });
    }
}

// Функция для отображения логов
function displayLogs(logs) {
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) return;
    
    // Сохраняем текущую позицию прокрутки
    const isScrolledToBottom = logsContainer.scrollHeight - logsContainer.clientHeight <= logsContainer.scrollTop + 1;
    
    // Получаем существующие логи из localStorage
    let existingLogs = [];
    try {
        const storedLogs = localStorage.getItem('storedLogs');
        if (storedLogs) {
            existingLogs = JSON.parse(storedLogs);
        }
    } catch (e) {
        console.warn('Ошибка при чтении логов из localStorage:', e);
    }
    
    // Добавляем только новые логи
    let newLogsAdded = 0;
    logs.forEach(log => {
        // Создаем уникальный ID для лога
        const logId = `${log.timestamp}-${log.level}-${log.message}`;
        
        // Проверяем, есть ли уже такой лог в контейнере по data-log-id
        const existingLog = logsContainer.querySelector(`[data-log-id="${logId}"]`);
        if (!existingLog) {
            const logEntry = document.createElement('div');
            logEntry.className = 'flex gap-4 log-entry';
            logEntry.setAttribute('data-log-id', logId);
            
            // Форматируем уровень лога
            let levelClass = '';
            let levelText = '';
            switch (log.level) {
                case 'INFO':
                    levelClass = 'text-green-500';
                    levelText = '[INFO]';
                    break;
                case 'WARNING':
                    levelClass = 'text-yellow-500';
                    levelText = '[WARN]';
                    break;
                case 'ERROR':
                    levelClass = 'text-red-500';
                    levelText = '[ERROR]';
                    break;
                case 'DEBUG':
                    levelClass = 'text-slate-500';
                    levelText = '[DEBUG]';
                    break;
                default:
                    levelClass = 'text-slate-500';
                    levelText = `[${log.level}]`;
            }
            
            logEntry.innerHTML = `
                <span class="text-slate-500 shrink-0">${log.timestamp}</span>
                <span class="${levelClass} font-bold shrink-0">${levelText}</span>
                <span class="text-slate-300">${log.message}</span>
            `;
            
            logsContainer.appendChild(logEntry);
            newLogsAdded++;
            
            // Добавляем лог в массив существующих логов
            existingLogs.push(log);
        }
    });
    
    // Ограничиваем количество логов в localStorage (например, последние 1000 записей)
    if (existingLogs.length > 1000) {
        existingLogs = existingLogs.slice(-1000);
    }
    
    // Сохраняем обновленные логи в localStorage
    try {
        localStorage.setItem('storedLogs', JSON.stringify(existingLogs));
    } catch (e) {
        console.warn('Ошибка при сохранении логов в localStorage:', e);
    }
    
    // Автопрокрутка если включена и если мы были внизу
    const autoScrollCheckbox = document.getElementById('auto-scroll-checkbox');
    if (autoScrollCheckbox && autoScrollCheckbox.checked && isScrolledToBottom) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

// Функция для загрузки логов
async function loadLogs() {
    try {
        const response = await fetch('./logs/output');
        if (response.ok) {
            const data = await response.json();
            displayLogs(data.logs);
        } else {
            console.error('Ошибка получения логов:', response.status);
        }
    } catch (error) {
        console.error('Ошибка сети при получении логов:', error);
    }
}

// Функция для восстановления логов из localStorage при загрузке вкладки "Логи"
function restoreLogsFromStorage() {
    try {
        const storedLogs = localStorage.getItem('storedLogs');
        if (storedLogs) {
            const logsContainer = document.getElementById('logs-container');
            if (logsContainer) {
                // Очищаем контейнер перед восстановлением
                logsContainer.innerHTML = '';
                
                const logs = JSON.parse(storedLogs);
                logs.forEach(log => {
                    // Создаем уникальный ID для лога
                    const logId = `${log.timestamp}-${log.level}-${log.message}`;
                    
                    const logEntry = document.createElement('div');
                    logEntry.className = 'flex gap-4 log-entry';
                    logEntry.setAttribute('data-log-id', logId);
                    
                    // Форматируем уровень лога
                    let levelClass = '';
                    let levelText = '';
                    switch (log.level) {
                        case 'INFO':
                            levelClass = 'text-green-500';
                            levelText = '[INFO]';
                            break;
                        case 'WARNING':
                            levelClass = 'text-yellow-500';
                            levelText = '[WARN]';
                            break;
                        case 'ERROR':
                            levelClass = 'text-red-500';
                            levelText = '[ERROR]';
                            break;
                        case 'DEBUG':
                            levelClass = 'text-slate-500';
                            levelText = '[DEBUG]';
                            break;
                        default:
                            levelClass = 'text-slate-500';
                            levelText = `[${log.level}]`;
                    }
                    
                    logEntry.innerHTML = `
                        <span class="text-slate-500 shrink-0">${log.timestamp}</span>
                        <span class="${levelClass} font-bold shrink-0">${levelText}</span>
                        <span class="text-slate-300">${log.message}</span>
                    `;
                    
                    logsContainer.appendChild(logEntry);
                });
            }
        }
    } catch (e) {
        console.warn('Ошибка при восстановлении логов из localStorage:', e);
    }
}

// Функция для обновления логов с интервалом
let logsInterval = null;

// Запуск обновления логов сразу при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Инициализируем события для текущей вкладки
    // Для вкладки устройств
    loadSerialPorts();
    setupDeviceScanButton();
    
    // Запускаем обновление логов в фоне
    startLogsUpdate();
});

function startLogsUpdate() {
    // Восстанавливаем логи из localStorage при старте
    restoreLogsFromStorage();
    
    // Загружаем логи сразу
    loadLogs();
    
    // Запускаем обновление каждые 2 секунды
    logsInterval = setInterval(loadLogs, 2000);
}

// Хранение ID последнего показанного лога для предотвращения дублирования
let lastDisplayedLogId = 0;

function startLogsUpdate() {
    // Загружаем логи сразу
    loadLogs();
    
    // Запускаем обновление каждые 2 секунды
    logsInterval = setInterval(loadLogs, 2000);
}

function stopLogsUpdate() {
    if (logsInterval) {
        clearInterval(logsInterval);
        logsInterval = null;
    }
}

// Обработка событий для вкладки логов
document.addEventListener('DOMContentLoaded', function () {
    // Обработка чекбокса автопрокрутки
    const autoScrollCheckbox = document.getElementById('auto-scroll-checkbox');
    if (autoScrollCheckbox) {
        autoScrollCheckbox.addEventListener('change', function() {
            if (this.checked) {
                const logsContainer = document.getElementById('logs-container');
                if (logsContainer) {
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }
            }
        });
    }
    
    // Обработка кнопки паузы
    const pauseButton = document.getElementById('pause-button');
    if (pauseButton) {
        pauseButton.addEventListener('click', function() {
            if (logsInterval) {
                stopLogsUpdate();
                this.innerHTML = '<span class="material-symbols-outlined text-lg">play_arrow</span> Воспроизвести';
            } else {
                startLogsUpdate();
                this.innerHTML = '<span class="material-symbols-outlined text-lg">pause</span> Пауза';
            }
        });
    }
    
    // Обработка кнопки очистки логов
    const clearButton = document.getElementById('clear-button');
    if (clearButton) {
        clearButton.addEventListener('click', async function() {
            if (confirm('Вы уверены, что хотите очистить логи?')) {
                // Здесь можно было бы отправить запрос на очистку логов, если бы был такой эндпоинт
                // Для сейчас просто очищаем отображение
                const logsContainer = document.getElementById('logs-container');
                if (logsContainer) {
                    logsContainer.innerHTML = '';
                }
                // Также очищаем localStorage
                try {
                    localStorage.removeItem('storedLogs');
                } catch (e) {
                    console.warn('Ошибка при очистке логов в localStorage:', e);
                }
            }
        });
    }
    
    // Обработка кнопки скачивания логов
    const downloadButton = document.getElementById('download-button');
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            // Для скачивания логов можно реализовать отдельный эндпоинт или использовать текущие логи
            alert('Функция скачивания логов пока не реализована');
        });
    }
    
    // Обработка переключения вкладок
    const tabLinks = document.querySelectorAll('.tab-link');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // При переходе на вкладку "Логи" восстанавливаем сохраненные логи
            if (this.getAttribute('href') === '/logs') {
                // Добавляем небольшую задержку для обеспечения корректной отрисовки
                setTimeout(() => {
                    restoreLogsFromStorage();
                }, 100);
            }
        });
    });
});
