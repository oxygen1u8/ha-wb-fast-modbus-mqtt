from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import logging

from app.lifespan import lifespan
from app.templates import templates, template_context
from app.routers import serial, devices, logs


logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="Wirenboard Modbus manager",
    version="0.1.0",
    lifespan=lifespan,
)


class IngressPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ingress_path = (
            request.headers.get("x-ingress-path")
            or request.headers.get("x-forwarded-prefix")
            or ""
        ).rstrip("/")
        if ingress_path:
            request.scope["root_path"] = ingress_path
        return await call_next(request)


app.add_middleware(IngressPathMiddleware)
app.mount(
    "/static",
    StaticFiles(directory=f"{Path(__file__).parent.resolve()}/static"),
    name="static",
)

app.include_router(serial.router)
app.include_router(devices.router)
app.include_router(logs.router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=template_context(request, content="", active_tab="home"),
    )
