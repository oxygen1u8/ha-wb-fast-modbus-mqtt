from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=f"{Path(__file__).parent.resolve()}/static/templates")
