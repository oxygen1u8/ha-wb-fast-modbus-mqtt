import aiofiles
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db_depends import get_async_db
from app.schemas.bus import Bus as BusSchema, BusCreate
from app.models.bus import Bus as BusModel
from app.schemas.conf import (
    ModbusConfiguration,
    ModbusConfigurationCreate,
    PortConfiguration,
)
from app.models.conf import ModbusConfigurationModel
from app.schemas.conf import DeviceConfiguration

router = APIRouter(prefix="/serial/bus", tags=["serial"])


@router.post("/sync", response_model=List[BusSchema])
async def create_bus_list(db: AsyncSession = Depends(get_async_db)):
    import json
    import os

    ports = []
    path_to_options = str(os.environ.get("PATH_TO_OPTIONS"))
    try:
        async with aiofiles.open(path_to_options, mode="r", encoding="utf-8") as file:
            content = await file.read()
            data = json.loads(content)
    except Exception as e:
        print(f"Error while reading file from PATH_TO_OPTIONS={path_to_options}: {e}")
        raise HTTPException(status_code=500)

    for config in data["Serial port config"]:
        ports.append(config["Port"])

    stmt = select(BusModel).where(BusModel.name.in_(ports))
    request = await db.scalars(stmt)
    bus_list = request.all()
    if len(bus_list) != len(ports):
        tmp = [
            BusModel(
                **BusCreate(
                    name=port, baudrate=[9600, 115200], parity=["N"]
                ).model_dump()
            )
            for port in ports
            if port not in [bus.name for bus in bus_list]
        ]
        db.add_all(tmp)
        await db.commit()
        request = await db.scalars(stmt)
        bus_list = request.all()

    return bus_list


@router.get("/{bus_id}", response_model=BusSchema)
async def get_bus_by_id(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    bus = await db.scalar(stmt)
    if bus is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist bus with bus_id={bus_id}"
        )
    return bus


@router.put("/{bus_id}", response_model=BusSchema)
async def update_bus(
    bus_id: int, bus: BusCreate, db: AsyncSession = Depends(get_async_db)
):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    db_bus = await db.scalar(stmt)
    if db_bus is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist bus with bus_id={bus_id}"
        )
    update_data = bus.model_dump(exclude_unset=True)
    await db.execute(
        update(BusModel).where(BusModel.id == bus_id).values(**update_data)
    )
    await db.commit()
    return await db.scalar(stmt)


@router.post("/bus/{bus_id}/scan")
async def scan_bus_by_id(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    return {}


@router.get("/bus/{bus_id}/devices", response_model=List[DeviceConfiguration])
async def get_bus_devices(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    bus = await db.scalar(stmt)
    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with bus_id={bus_id} not exists",
        )
    return {}
