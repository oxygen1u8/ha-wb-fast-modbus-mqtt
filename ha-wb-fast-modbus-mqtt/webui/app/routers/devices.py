from fastapi import APIRouter, Request
from app.templates import templates, template_context


router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
@router.get("/")
async def root(request: Request):
    content = templates.TemplateResponse(
        name="modules/devices.html", context=template_context(request)
    ).body.decode("utf-8")

    return templates.TemplateResponse(
        name="index.html",
        context=template_context(request, content=content, active_tab="devices"),
    )
