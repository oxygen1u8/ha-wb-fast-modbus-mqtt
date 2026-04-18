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
        if (!response.ok) {
            console.error('Ошибка получения списка портов:', response.status);
        } else {
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
