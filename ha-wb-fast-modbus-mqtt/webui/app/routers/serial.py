from fastapi import APIRouter, Request
from app.templates import templates, template_context

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
