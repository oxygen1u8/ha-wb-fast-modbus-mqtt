from sqlalchemy import select, update, insert, delete, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request, Depends, HTTPException
from app.templates import templates, template_context
from app.models.template import Template as TemplateModel
from app.models.device import Device as DeviceModel
from app.schemas.json import JSONContent
from app.schemas.device import Device as DeviceSchema
from app.db_depends import get_async_db
from typing import List
import logging


router = APIRouter(prefix="/devices", tags=["devices"])


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


@router.get("/templates/type", response_model=List[str])
async def get_templates_type(db: AsyncSession = Depends(get_async_db)):
    stmt = select(TemplateModel.device_type)
    titles = await db.scalars(stmt)
    return titles.all()


@router.get("/{device_id}/config", response_model=str)
async def get_device_config(device_id: int, db: AsyncSession = Depends(get_async_db)):
    stmt = select(DeviceModel).where(DeviceModel.id == device_id)
    device = await db.scalar(stmt)
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist device with device_id={device_id}"
        )
    return device.config


@router.put("/{device_id}/config", response_model=DeviceSchema)
async def update_device_config(
    device_id: int, config: JSONContent, db: AsyncSession = Depends(get_async_db)
):
    stmt = select(DeviceModel).where(DeviceModel.id == device_id)
    device = await db.scalar(stmt)
    if device is None:
        raise HTTPException(
            status_code=404, detail=f"Non-exist device with device_id={device_id}"
        )
    device.config = config.content
    await db.commit()
    await db.refresh(device)
    return device
