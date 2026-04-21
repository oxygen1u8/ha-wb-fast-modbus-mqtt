from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(
    directory=f"{Path(__file__).parent.resolve()}/static/templates"
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
        **context,
    }
