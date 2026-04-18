from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Optional
from pathlib import Path
import logging

from app.templates import templates
from app.routers import serial, devices, logs


logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="Wirenboard Modbus manager",
    version="0.1.0",
)
app.mount(
    "/static",
    StaticFiles(directory=f"{Path(__file__).parent.resolve()}/static"),
    name="static",
)

app.include_router(serial.router)
app.include_router(devices.router)
app.include_router(logs.router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": ""},
    )
