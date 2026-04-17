from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Optional
import logging


app = FastAPI(
    title="Wirenboard Modbus manager",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=f"app/static"), name="static")
templates = Jinja2Templates(directory=f"app/static/templates")


logging.basicConfig(level=logging.INFO)


@app.get("/")
async def root(
    request: Request,
    page: Optional[str] = Query(None, description="Page select")
):
    content = ""
    active_tab = ""
    if page is not None:
        content = templates.TemplateResponse(
            request=request, name=f"modules/{page}.html", context={}
        ).body.decode("utf-8")
        active_tab = page

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"content": content, "active_tab": page},
    )
