from fastapi import APIRouter, Request, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.templates import templates
from app.db_depends import get_async_db
from typing import List
from app.schemas.bus import Bus as BusSchema
from app.schemas.device import Device as DeviceSchema


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
    pass


@router.get("/bus/{bus_id}", response_model=List[DeviceSchema])
async def get_bus_devices(bus_id: int, db: AsyncSession = Depends(get_async_db)):
    pass


@router.post(
    "/scan", response_model=List[DeviceSchema], status_code=status.HTTP_201_CREATED
)
async def scan(db: AsyncSession = Depends(get_async_db)):
    pass
