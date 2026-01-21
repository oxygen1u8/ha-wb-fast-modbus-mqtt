from fastmodbus.manager import WirenboardModbusManager
from pymodbus.pdu.decoders import *
import asyncio
import time
import json
import argparse
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging

# Глобальная переменная для хранения пути к конфигурации
path_to_options = "config.json"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fast Modbus Scanner", version="1.0.0")
templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Глобальная переменная для хранения логов
scan_logs = []


async def execute_scan(manager: WirenboardModbusManager):
    t = time.time()
    slave_map = await manager.scan_bus()
    t = time.time() - t
    log_message = f"[{manager.port}]: scan took {t} s"
    logger.info(log_message)
    if not len(slave_map):
        log_message = f"[{manager.port}]: no Fast Modbus device found\n"
        logger.info(log_message)
        scan_logs.append(log_message)
    else:
        for slave in slave_map:
            log_message = f"Device name: {slave.device_name}\n"
            log_message += f"Firmware Version: {slave.firmware_version}\n"
            log_message += f"Slave ID: {hex(slave.slave_id)} ({slave.slave_id})\n"
            log_message += f"Serial Number: {hex(slave.serial_num)} ({slave.serial_num})\n"
            log_message += f"Baudrate: {slave.baudrate} bps\n"
            log_message += f"Parity: {slave.parity}\n"
            logger.info(f"[{manager.port}]: ", log_message)
            scan_logs.append(log_message)


async def run_scans(options_path: str, specific_port: str = None):
    # Если указан конкретный порт, используем только его
    if specific_port:
        ports = [{"Port": specific_port}]
    else:
        ports = data["Serial port config"]

    port_managers = [
        WirenboardModbusManager(port["Port"], baudrates=[9600, 115200], parity_options=["N"]) for port in ports
    ]

    results = await asyncio.gather(
        *[asyncio.create_task(execute_scan(manager)) for manager in port_managers]
    )

    return results


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "logs": scan_logs}
    )


@app.post("/scan")
async def start_scan(
    background_tasks: BackgroundTasks,
    port: str = None
):
    """API endpoint для запуска сканирования"""
    logger.info(f"Starting scan with options from {path_to_options}")
    if port:
        logger.info(f"Scanning specific port: {port}")

    # Очищаем предыдущие логи
    global scan_logs
    scan_logs.clear()

    # Добавляем сообщение о начале сканирования
    scan_logs.append("Начало сканирования...")

    # Запускаем сканирование в фоне
    background_tasks.add_task(run_scans, path_to_options, port)

    return {"status": "scan started"}


@app.get("/logs")
async def get_logs():
    """API endpoint для получения логов"""
    return {"logs": scan_logs}

@app.get("/ports")
async def get_ports():
    """API endpoint для получения списка портов"""
    try:
        with open(path_to_options, "r", encoding="utf-8") as f:
            data = json.load(f)
        ports = [port["Port"] for port in data["Serial port config"] if port.get("Port") and port["Port"].strip()]
        logger.info(ports)
        return {"ports": ports}
    except Exception as e:
        return {"ports": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    import os

    parser = argparse.ArgumentParser(description="Fast Modbus")
    parser.add_argument("--options", type=str, help="Путь до options.json")

    args = parser.parse_args()
    path_to_options = args.options

    with open(path_to_options, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Получаем порт из переменной окружения, если она установлена (для Home Assistant ingress)
    port = int(os.environ.get("PORT", 8000))
    
    # Запускаем веб-сервер
    uvicorn.run(app, host="0.0.0.0", port=port)
