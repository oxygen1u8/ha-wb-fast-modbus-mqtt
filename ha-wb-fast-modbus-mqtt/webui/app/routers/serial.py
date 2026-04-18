from fastapi import APIRouter, Request
from app.templates import templates


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
