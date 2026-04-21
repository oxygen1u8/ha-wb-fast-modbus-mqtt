from fastapi.templating import Jinja2Templates
from pathlib import Path

APP_DIR = Path(__file__).parent.resolve()
STATIC_DIR = APP_DIR / "static"

templates = Jinja2Templates(
    directory=str(STATIC_DIR / "templates")
)


def get_app_base_path(request):
    request_path = request.url.path.rstrip("/")
    if not request_path:
        return ""

    for suffix in ("/devices", "/serial", "/logs"):
        if request_path.endswith(suffix):
            return request_path[: -len(suffix)]

    return request_path


def template_context(request, **context):
    app_base_path = get_app_base_path(request)
    return {
        "request": request,
        "root_path": request.scope.get("root_path", "").rstrip("/"),
        "app_base_path": app_base_path,
        "inline_style": (STATIC_DIR / "style.css").read_text(encoding="utf-8"),
        "inline_script": (STATIC_DIR / "script.js").read_text(encoding="utf-8"),
        **context,
    }
