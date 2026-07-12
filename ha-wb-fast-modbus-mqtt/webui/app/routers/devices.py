from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request, Depends, HTTPException, Body
from app.templates import templates, template_context
from app.models.template import Template as TemplateModel
from app.models.conf import ModbusConfigurationModel
from app.schemas.conf import (
    DeviceConfigurationRequest,
    DeviceConfiguration,
    DeviceSetConfigurationRequest,
    ModbusConfiguration,
    ModbusConfigurationCreate,
)
from app.db_depends import get_async_db
from app.logger import get_logger
from typing import List, Any, Dict
import json


router = APIRouter(prefix="/devices", tags=["devices"])
logger = get_logger(__name__)


@router.get("")
@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        request=request,
        name="modules/devices.html",
        context=template_context(request),
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=template_context(request, content=content, active_tab="devices"),
    )


@router.get("/templates/type")
async def get_templates_type(db: AsyncSession = Depends(get_async_db)):
    stmt = select(TemplateModel.device_type)
    titles = await db.scalars(stmt)
    return titles.all()


@router.get("/config/{port_path}/{device_id}", response_model=DeviceConfiguration)
async def get_device_config(
    port_path: str, device_id: int, db: AsyncSession = Depends(get_async_db)
):
    stmt = select(ModbusConfigurationModel)
    modbus_configuration = await db.scalar(stmt)
    if modbus_configuration is None:
        raise HTTPException(
            status_code=404, detail="Modbus configuration is not exists"
        )
    json_modbus_configuration = json.loads(modbus_configuration.config)
    schema_modbus_configuration = ModbusConfigurationCreate(**json_modbus_configuration)
    port = None
    for _ in schema_modbus_configuration.ports:
        if _.path == port_path:
            port = _
            break
    if port is None:
        raise HTTPException(
            status_code=404,
            detail=f"Undefined port with path: {port_path}",
        )
    device = None
    for _ in port.devices:
        if _.id == device_id:
            device = _
            break
    if device is None:
        raise HTTPException(
            status_code=404,
            detail=f"Undefined device with id = {device_id}",
        )
    return device


@router.post("/config")
async def set_device_config(
    setup_config: DeviceSetConfigurationRequest,
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(ModbusConfigurationModel)
    modbus_configuration = await db.scalar(stmt)
    if modbus_configuration is None:
        raise HTTPException(
            status_code=404, detail="Modbus configuration is not exists"
        )
    json_modbus_configuration = json.loads(modbus_configuration.config)
    schema_modbus_configuration = ModbusConfigurationCreate(**json_modbus_configuration)
    port = None
    for _ in schema_modbus_configuration.ports:
        if _.path == setup_config.port_path:
            port = _
            break
    if port is None:
        raise HTTPException(
            status_code=404,
            detail=f"Undefined port with path: {setup_config.port_path}",
        )
    device = None
    for _ in port.devices:
        if _.id == setup_config.config.id:
            device = _
            break
    if device is None:
        port.devices.append(setup_config.config)
    else:
        device = setup_config.config
    modbus_configuration.config = schema_modbus_configuration.model_dump_json()
    await db.commit()
    return setup_config.config
