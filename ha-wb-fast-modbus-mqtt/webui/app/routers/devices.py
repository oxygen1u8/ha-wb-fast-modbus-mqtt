from sqlalchemy import select, update, insert, delete, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request, Depends
from app.templates import templates, template_context
from app.models.templates import Template as TemplateModel
from app.db_depends import get_async_db
from typing import List
import logging


router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/templates/type", response_model=List[str])
async def get_templates_type(db: AsyncSession = Depends(get_async_db)):
    stmt = select(TemplateModel.device_type)
    titles = await db.scalars(stmt)
    return titles.all()


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
