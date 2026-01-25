from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastmodbus.manager import WirenboardModbusManager
from .models import BusConfig, DeviceInfo, ResponseScan, ResponsePorts
import logging
from pathlib import Path

app = FastAPI(title="Wirenboard Modbus manager", version="0.1.0")
templates = Jinja2Templates(directory=f"{Path(__file__).parent.resolve()}/templates")
app.mount("/static", StaticFiles(directory=f"{Path(__file__).parent.resolve()}/static", html=True), name="static")


logging.basicConfig(level=logging.INFO)


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/ports", response_model=ResponsePorts)
def get_ports():
    if not hasattr(app, 'ports'):
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
