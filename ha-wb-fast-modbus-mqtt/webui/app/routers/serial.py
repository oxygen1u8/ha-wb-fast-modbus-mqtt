import aiofiles
import logging
from typing import List
from fastapi import APIRouter, Request, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete, bindparam
from app.templates import templates, template_context
from app.db_depends import get_async_db
from app.schemas.bus import Bus as BusSchema, BusCreate
from app.schemas.device import Device as DeviceSchema, DeviceCreate, DeviceListDelete
from app.models.bus import Bus as BusModel
from app.models.device import Device as DeviceModel
from app.fastmodbus.manager import WirenboardModbusManager, WirenboardModbusSlave


router = APIRouter(prefix="/serial", tags=["serial"])


@router.get("")
@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        request=request,
        name="modules/serial.html",
        context=template_context(request),
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=template_context(request, content=content, active_tab="serial"),
    )


@router.post("/sync", response_model=List[BusSchema])
async def create_bus_list(db: AsyncSession = Depends(get_async_db)):
    import json
    import os

    ports = []
    try:
        path_to_options = os.environ.get("PATH_TO_OPTIONS")
        async with aiofiles.open(path_to_options, "r", encoding="utf-8") as file:
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


@router.get("/bus/{bus_id}", response_model=BusSchema)
async def get_bus_by_id(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    bus = await db.scalar(stmt)
    if bus is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist bus with bus_id={bus_id}"
        )
    return bus


@router.put("/bus/{bus_id}", response_model=BusSchema)
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


@router.get("/bus/{bus_id}/devices", response_model=List[DeviceSchema])
async def get_bus_devices(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    bus = await db.scalar(stmt)
    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with bus_id={bus_id} not exists",
        )
    stmt = select(DeviceModel).where(DeviceModel.bus_id == bus_id)
    devices = await db.scalars(stmt)
    return devices.all()


@router.post(
    "/devices",
    response_model=List[DeviceSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_bus_devices(
    devices: List[DeviceCreate], db: AsyncSession = Depends(get_async_db)
):
    stmt = select(DeviceModel).where(
        DeviceModel.serial_num.in_([device.serial_num for device in devices]),
    )
    db_devices = await db.scalars(stmt)
    if len(db_devices.all()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Some of devices already exists within database",
        )

    db_devices = [DeviceModel(**device.model_dump()) for device in devices]
    db.add_all(db_devices)
    await db.commit()
    return db_devices


@router.put("/bus/{bus_id}/devices", response_model=List[DeviceSchema])
async def update_bus_devices(
    bus_id: int, devices: List[DeviceCreate], db: AsyncSession = Depends(get_async_db)
):
    stmt = select(DeviceModel).where(
        DeviceModel.bus_id == bus_id,
        DeviceModel.serial_num.in_([device.serial_num for device in devices]),
    )
    db_devices = (await db.scalars(stmt)).all()
    if len(db_devices) != len(devices):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some of devices wasn't found within database",
        )
    update_stmt = (
        update(DeviceModel)
        .where(
            DeviceModel.bus_id == bindparam("bus_id_param"),
            DeviceModel.serial_num == bindparam("serial_num_param"),
        )
        .values(
            model=bindparam("model"),
            baudrate=bindparam("baudrate"),
            parity=bindparam("parity"),
            slave_address=bindparam("slave_address"),
        )
    )

    await db.execute(
        update_stmt,
        [
            {
                "bus_id_param": bus_id,
                "serial_num_param": device.serial_num,
                **device.model_dump(exclude={"bus_id", "serial_num"}),
            }
            for device in devices
        ],
    )
    await db.commit()
    updated_devices = await db.scalars(stmt)
    return updated_devices.all()


@router.delete("/devices")
async def delete_bus_devices(
    request: DeviceListDelete, db: AsyncSession = Depends(get_async_db)
):
    stmt = delete(DeviceModel).where(DeviceModel.id.in_(request.devices_id))
    await db.execute(stmt)
    await db.commit()


@router.post("/bus/{bus_id}/scan", response_model=List[DeviceCreate])
async def scan_bus_by_id(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(BusModel).where(BusModel.id == bus_id)
    bus = await db.scalar(stmt)

    if bus is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist bus with bus_id={bus_id}"
        )

    try:
        logging.info("Start scan on:")
        logging.info(f"Port: {bus.name}")
        logging.info(f"Baudrate: {bus.baudrate}")
        logging.info(f"Parity: {bus.parity}")

        manager = WirenboardModbusManager(bus.name, bus.baudrate, bus.parity)
        slave_list = await manager.scan_bus()
    except Exception as e:
        logging.error(f"Scanning error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scan bus with bus_id={bus_id}",
        )

    device_list = [
        DeviceCreate(
            model=slave.device_name,
            baudrate=slave.baudrate,
            parity=slave.parity,
            slave_address=slave.slave_id,
            serial_num=slave.serial_num,
            bus_id=bus_id,
        ).model_dump()
        for slave in slave_list
    ]

    return device_list
