from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from app.database import async_session_maker
from app.models.templates import Template
import json
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    path_to_templates = os.environ.get("PATH_TO_TEMPLATES")
    if path_to_templates:
        templates_dir = Path(path_to_templates)
        if templates_dir.is_dir():
            async with async_session_maker() as session:
                templates_list = sorted(templates_dir.glob("*.json"))
                stmt = select(Template.filename)
                db_templates_list = await session.scalars(stmt)
                db_templates_list = db_templates_list.all()
                if len(db_templates_list) != len(templates_list):
                    for template_path in templates_list:
                        with template_path.open(encoding="utf-8") as template_file:
                            template_config = json.load(template_file)
                        device_type = template_config["device_type"]
                        config = json.dumps(
                            template_config,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                        statement = insert(Template).values(
                            device_type=device_type,
                            title=template_config.get("title"),
                            filename=template_path.name,
                            config=config,
                        )
                        statement = statement.on_conflict_do_update(
                            index_elements=[Template.device_type],
                            set_={
                                "title": statement.excluded.title,
                                "filename": statement.excluded.filename,
                                "config": statement.excluded.config,
                            },
                        )

                    await session.execute(statement)
                await session.commit()
    yield
