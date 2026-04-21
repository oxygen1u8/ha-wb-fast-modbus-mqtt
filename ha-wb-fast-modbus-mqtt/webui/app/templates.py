from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(
    directory=f"{Path(__file__).parent.resolve()}/static/templates"
)


def template_context(request, **context):
    return {
        "request": request,
        "root_path": request.scope.get("root_path", "").rstrip("/"),
        **context,
    }
