from typing import List
from fastapi import APIRouter, Request, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.templates import templates
from app.db_depends import get_async_db
from app.schemas.bus import Bus as BusSchema, BusCreate
from app.schemas.device import Device as DeviceSchema
from app.models.bus import Bus as BusModel
from app.models.device import Device as DeviceModel

import logging


router = APIRouter(prefix="/serial", tags=["serial"])


@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        request=request, name="modules/serial.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": content, "active_tab": "serial"},
    )


@router.get("/bus", response_model=List[BusSchema])
async def get_bus(db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel)
    bus_list = await db.scalars(stmt)
    bus_list = bus_list.all()
    if len(bus_list) == 0:
        import json
        import os

        path_to_options = os.environ.get("PATH_TO_OPTIONS")
        ports = []

        try:
            with open(path_to_options, "r", encoding="utf-8") as f:
                data = json.load(f)
            for config in data["Serial port config"]:
                ports.append(config["Port"])
        except Exception as e:
            print(f"Ошибка при чтении конфигурации портов: {e}")

        tmp = []
        for port in ports:
            bus_list.append(
                BusCreate(
                    name=port,
                    baudrate=[9600, 115200],
                    parity=["N"]
                )
            )
        bus_list = [BusModel(**bus.model_dump()) for bus in bus_list]
        db.add_all(bus_list)
        await db.commit()
    
    return bus_list


@router.put("/bus", response_model=BusSchema)
async def update_bus(bus: BusSchema, db: AsyncSession = Depends(get_async_db)):
    pass


@router.get("/bus/{bus_id}", response_model=List[DeviceSchema])
async def get_bus_devices(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    pass


@router.post(
    "/scan", response_model=List[DeviceSchema], status_code=status.HTTP_201_CREATED
)
async def scan(db: AsyncSession = Depends(get_async_db)):
    pass
