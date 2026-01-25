from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastmodbus.manager import WirenboardModbusManager
from .models import BusConfig, DeviceInfo, ResponseScan, ResponsePorts
import logging
import time
from pathlib import Path
from .log import LogCaptureHandler

log_capture_handler = LogCaptureHandler()

app = FastAPI(title="Wirenboard Modbus manager", version="0.1.0")
templates = Jinja2Templates(directory=f"{Path(__file__).parent.resolve()}/templates")
app.mount(
    "/static",
    StaticFiles(directory=f"{Path(__file__).parent.resolve()}/static", html=True),
    name="static",
)

logging.basicConfig(level=logging.INFO, handlers=[log_capture_handler])


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": "", "active_tab": "devices"},
    )


@app.get("/serial")
async def serial(request: Request):
    device_content = templates.TemplateResponse(
        request=request, name="modules/serial.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": device_content, "active_tab": "serial"},
    )


@app.get("/devices")
async def devices(request: Request):
    settings_content = templates.TemplateResponse(
        request=request, name="modules/devices.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": settings_content, "active_tab": "devices"},
    )


@app.get("/logs")
async def logs(request: Request):
    logs_content = templates.TemplateResponse(
        request=request, name="modules/logs.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": logs_content, "active_tab": "logs"},
    )


@app.get("/ports", response_model=ResponsePorts)
def get_ports():
    if not hasattr(app, "ports"):
        app.ports = []
    logging.info(f"Response: {app.ports}")
    return ResponsePorts(port_list=app.ports)


@app.post("/scan", response_model=ResponseScan)
async def scan(config: BusConfig):
    try:
        logging.info(f"Start scan on:")
        logging.info(f"Port: {config.port}")
        logging.info(f"Baudrate: {config.baudrate}")
        logging.info(f"Parity: {config.parity}")

        if not len(config.baudrate):
            return ResponseScan(slave_list=None)

        manager = WirenboardModbusManager(config.port, config.baudrate, config.parity)
        slave_list = await manager.scan_bus()
        response = []
        for slave in slave_list:
            logging.info(f"[{manager.port}]: {slave}")
            response.append(
                DeviceInfo(
                    slave_name=slave.device_name,
                    firmware_version=slave.firmware_version,
                    slave_id=slave.slave_id,
                    serial_num=slave.serial_num,
                    baudrate=slave.baudrate,
                    parity=slave.parity,
                )
            )
        return ResponseScan(slave_list=response)
    except Exception as e:
        logging.error(f"Ошибка при сканировании: {e}")
        return ResponseScan(slave_list=None)



@app.get("/logs/output")
def get_logs():
    # Ограничиваем количество логов, отправляемых на фронтенд (последние 100 записей)
    max_logs = 100
    recent_logs = log_capture_handler.log_records[-max_logs:] if log_capture_handler.log_records else []
    
    logs = []
    for record in recent_logs:
        # Используем правильный способ получения времени записи лога
        timestamp = getattr(record, 'asctime', None)
        if timestamp is None:
            # Если asctime отсутствует, форматируем время вручную
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
        logs.append(
            {
                "timestamp": timestamp,
                "level": record.levelname,
                "message": record.getMessage(),
            }
        )
    log_capture_handler.log_records.clear()
    return {"logs": logs}
