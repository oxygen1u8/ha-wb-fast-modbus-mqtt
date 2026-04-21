window.tailwind = window.tailwind || {};
window.tailwind.config = {
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

const BAUDRATE_OPTIONS = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200];
const PARITY_OPTIONS = [
    { value: "N", label: "Нет (None)" },
    { value: "E", label: "Чет (Even)" },
    { value: "O", label: "Нечет (Odd)" },
];
const APP_BASE_PATH = (document.body?.dataset.basePath || "").replace(/\/$/, "");

function buildAppUrl(path) {
    if (!path.startsWith("/")) {
        throw new Error(`Application path must start with '/': ${path}`);
    }
    return `${APP_BASE_PATH}${path}`;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        let details = "";
        try {
            const errorData = await response.json();
            details = errorData.detail ? `: ${errorData.detail}` : "";
        } catch {
            details = "";
        }
        throw new Error(`HTTP ${response.status}${details}`);
    }
    return response.json();
}

function getSelectedValues(selector) {
    return Array.from(document.querySelectorAll(selector))
        .filter((input) => input.checked)
        .map((input) => input.value);
}

function renderBaudrateOptions(selectedValues = []) {
    const container = document.getElementById("baudrate-options");
    if (!container) {
        return;
    }

    const selectedSet = new Set(selectedValues.map(String));
    container.innerHTML = BAUDRATE_OPTIONS.map((baudrate) => `
        <label class="flex flex-col items-center justify-center p-4 border border-slate-200 dark:border-border-dark rounded-lg hover:border-primary/50 dark:hover:border-primary/50 cursor-pointer group transition-all bg-slate-50/50 dark:bg-background-dark/50">
            <input class="sr-only peer baudrate-checkbox" value="${baudrate}" type="checkbox" ${selectedSet.has(String(baudrate)) ? "checked" : ""} />
            <div class="w-5 h-5 border-2 border-slate-300 dark:border-slate-600 rounded flex items-center justify-center mb-3 peer-checked:bg-primary peer-checked:border-primary transition-colors">
                <span class="material-symbols-outlined text-white text-xs scale-0 peer-checked:scale-100 transition-transform">check</span>
            </div>
            <span class="text-sm font-mono font-bold text-slate-600 dark:text-slate-400 group-hover:text-primary transition-colors">${baudrate}</span>
        </label>
    `).join("");
}

function renderParityOptions(selectedValues = []) {
    const container = document.getElementById("parity-options");
    if (!container) {
        return;
    }

    const selectedSet = new Set(selectedValues);
    container.innerHTML = PARITY_OPTIONS.map((parity) => `
        <label class="flex items-center gap-3 cursor-pointer group">
            <input
                class="w-5 h-5 rounded border-slate-300 dark:border-border-dark text-primary focus:ring-primary dark:bg-background-dark parity-checkbox"
                type="checkbox"
                value="${parity.value}"
                ${selectedSet.has(parity.value) ? "checked" : ""}
            />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-primary transition-colors">${parity.label}</span>
        </label>
    `).join("");
}

function updateDevicesTable(devices) {
    const tableBody = document.getElementById("devices-table-body");
    const emptyState = document.getElementById("devices-empty-state");

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = "";

    if (!devices.length) {
        if (emptyState) {
            emptyState.classList.remove("hidden");
        }
        return;
    }

    if (emptyState) {
        emptyState.classList.add("hidden");
    }

    devices.forEach((device) => {
        const row = document.createElement("tr");
        row.className = "hover:bg-slate-50 dark:hover:bg-border-dark/20 transition-colors";

        const model = device.model || "Неизвестно";
        const slaveAddress = Number(device.slave_address);
        const serialNum = Number(device.serial_num);

        row.innerHTML = `
            <td class="px-6 py-4">
                <div class="text-sm font-bold text-slate-900 dark:text-white">${escapeHtml(model)}</div>
            </td>
            <td class="px-6 py-4 text-sm font-mono text-slate-600 dark:text-slate-400">0x${slaveAddress.toString(16).toUpperCase()} (${slaveAddress})</td>
            <td class="px-6 py-4 text-sm font-mono text-slate-600 dark:text-slate-400">0x${serialNum.toString(16).toUpperCase().padStart(8, "0")}</td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">${device.baudrate || "Нет данных"}</td>
            <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">${device.parity || "Нет данных"}</td>
            <td class="px-6 py-4 text-right text-sm text-slate-400">bus #${device.bus_id}</td>
        `;

        tableBody.appendChild(row);
    });
}

function setStatus(message, tone = "muted") {
    const node = document.getElementById("serial-status");
    if (!node) {
        return;
    }

    node.textContent = message;
    node.className = "text-sm";

    if (tone === "error") {
        node.classList.add("text-rose-500");
        return;
    }

    if (tone === "success") {
        node.classList.add("text-emerald-500");
        return;
    }

    node.classList.add("text-slate-500", "dark:text-slate-400");
}

function setBusy(isBusy) {
    const scanButton = document.getElementById("scan-button");
    const saveButton = document.getElementById("save-button");
    const portSelect = document.getElementById("port-select");

    [scanButton, saveButton, portSelect].forEach((element) => {
        if (element) {
            element.disabled = isBusy;
        }
    });
}

async function loadBusDevices(busId) {
    return requestJson(buildAppUrl(`/serial/bus/${busId}/devices`));
}

function renderBusOptions(buses, selectedBusId) {
    const portSelect = document.getElementById("port-select");
    if (!portSelect) {
        return;
    }

    portSelect.innerHTML = "";

    buses.forEach((bus) => {
        const option = document.createElement("option");
        option.value = bus.id;
        option.textContent = bus.name;
        option.selected = String(bus.id) === String(selectedBusId);
        portSelect.appendChild(option);
    });
}

async function loadBuses() {
    return requestJson(buildAppUrl("/serial/bus"));
}

function renderSerialPageState(buses, activeBusId, devices) {
    const activeBus = buses.find((bus) => String(bus.id) === String(activeBusId));
    if (!activeBus) {
        updateDevicesTable([]);
        setStatus("Шина не найдена", "error");
        return;
    }

    renderBusOptions(buses, activeBus.id);
    renderBaudrateOptions(activeBus.baudrate || []);
    renderParityOptions(activeBus.parity || []);
    updateDevicesTable(devices);
}

async function syncBusState(busId, buses) {
    const activeBus = buses.find((bus) => String(bus.id) === String(busId));
    if (!activeBus) {
        updateDevicesTable([]);
        setStatus("Шина не найдена", "error");
        return;
    }

    const devices = await loadBusDevices(activeBus.id);
    renderSerialPageState(buses, activeBus.id, devices);
    setStatus(`Загружена шина ${activeBus.name}`);
}

async function saveBusSettings(buses) {
    const portSelect = document.getElementById("port-select");
    const selectedBus = buses.find((bus) => String(bus.id) === portSelect?.value);

    if (!selectedBus) {
        setStatus("Сначала выберите шину", "error");
        return buses;
    }

    const payload = {
        name: selectedBus.name,
        baudrate: getSelectedValues(".baudrate-checkbox").map(Number),
        parity: getSelectedValues(".parity-checkbox"),
    };

    setBusy(true);
    setStatus("Сохраняю настройки шины...");

    try {
        await requestJson(buildAppUrl(`/serial/bus/${selectedBus.id}`), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const nextBuses = await loadBuses();
        document.getElementById("port-select").value = String(selectedBus.id);
        await syncBusState(selectedBus.id, nextBuses);
        setStatus("Настройки шины сохранены", "success");
        return nextBuses;
    } catch (error) {
        console.error("Ошибка сохранения шины:", error);
        setStatus(`Не удалось сохранить настройки: ${error.message}`, "error");
        return buses;
    } finally {
        setBusy(false);
    }
}

async function scanSelectedBus() {
    const portSelect = document.getElementById("port-select");
    const busId = portSelect?.value;

    if (!busId) {
        setStatus("Сначала выберите шину", "error");
        return;
    }

    setBusy(true);
    setStatus("Идёт сканирование шины...");

    try {
        const devices = await requestJson(buildAppUrl(`/serial/bus/${busId}/scan`), {
            method: "POST",
        });
        updateDevicesTable(devices);
        setStatus(`Сканирование завершено. Найдено устройств: ${devices.length}`, "success");
    } catch (error) {
        console.error("Ошибка сканирования:", error);
        setStatus(`Не удалось просканировать шину: ${error.message}`, "error");
    } finally {
        setBusy(false);
    }
}

async function initSerialPage() {
    const portSelect = document.getElementById("port-select");
    if (!portSelect) {
        return;
    }

    setBusy(true);
    setStatus("Загружаю конфигурацию шин...");

    let buses = [];

    try {
        buses = await loadBuses();

        if (!buses.length) {
            updateDevicesTable([]);
            renderBaudrateOptions([]);
            renderParityOptions([]);
            setStatus("Шины не найдены", "error");
            return;
        }

        const initialBus = buses[0];
        const devices = await loadBusDevices(initialBus.id);
        renderSerialPageState(buses, initialBus.id, devices);
        setStatus(`Загружена шина ${initialBus.name}`);
    } catch (error) {
        console.error("Ошибка инициализации serial-страницы:", error);
        setStatus(`Не удалось загрузить шины: ${error.message}`, "error");
        return;
    } finally {
        setBusy(false);
    }

    portSelect.addEventListener("change", async (event) => {
        setBusy(true);
        setStatus("Переключаю активную шину...");
        try {
            await syncBusState(event.target.value, buses);
        } catch (error) {
            console.error("Ошибка переключения шины:", error);
            setStatus(`Не удалось загрузить устройства: ${error.message}`, "error");
        } finally {
            setBusy(false);
        }
    });

    document.getElementById("scan-button")?.addEventListener("click", () => {
        scanSelectedBus();
    });

    document.getElementById("save-button")?.addEventListener("click", async () => {
        buses = await saveBusSettings(buses);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initSerialPage();
});
