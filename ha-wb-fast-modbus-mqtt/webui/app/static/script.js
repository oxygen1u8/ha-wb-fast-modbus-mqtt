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

            // Очищаем существующие опции
            portSelect.innerHTML = '';

            // Добавляем новые опции
            data.port_list.forEach(port => {
                const option = document.createElement('option');
                option.value = port;
                option.textContent = port;
                portSelect.appendChild(option);
            });
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

// Логика для кнопки сканирования шины
document.addEventListener('DOMContentLoaded', function () {
    // Загружаем список портов при загрузке страницы
    loadSerialPorts();

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
});