from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.templates import templates


router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)


@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        request=request, name="modules/logs.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": content, "active_tab": "logs"},
    )
