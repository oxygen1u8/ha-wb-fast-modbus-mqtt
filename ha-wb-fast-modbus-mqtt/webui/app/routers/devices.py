from fastapi import APIRouter, Request
from app.templates import templates


router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        request=request, name="modules/devices.html", context={}
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": content, "active_tab": "devices"},
    )
