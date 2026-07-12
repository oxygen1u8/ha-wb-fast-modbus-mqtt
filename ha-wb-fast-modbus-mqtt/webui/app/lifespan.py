import asyncio
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from typing import List
from app.database import async_session_maker
from app.models.template import Template
from app.models.conf import ModbusConfigurationModel
from app.schemas.conf import ModbusConfigurationCreate, PortConfiguration
from app.handle.handle import ModbusHandle, handle_list
import json
import os
import aiofiles


async def load_templates():
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


async def load_main_config():
    async with async_session_maker() as session:
        stmt = select(ModbusConfigurationModel)
        modbus_config = await session.scalar(stmt)
        if modbus_config is None:
            session.add(
                ModbusConfigurationModel(
                    config=ModbusConfigurationCreate().model_dump_json()
                )
            )
            await session.commit()


async def load_serial_ports():
    global handle_list
    ports = []
    path_to_options = str(os.environ.get("PATH_TO_OPTIONS"))
    try:
        async with aiofiles.open(path_to_options, mode="r", encoding="utf-8") as file:
            content = await file.read()
            data = json.loads(content)
    except Exception as e:
        print(f"Error while reading file from PATH_TO_OPTIONS={path_to_options}: {e}")
        raise FileExistsError("TODO")

    for config in data["Serial port config"]:
        ports.append(config["Port"])

    async with async_session_maker() as session:
        stmt = select(ModbusConfigurationModel)
        modbus_model = await session.scalar(stmt)

        if modbus_model is None:
            raise RuntimeError("TODO")

        json_modbus_model = json.loads(modbus_model.config)
        json_port_list = json_modbus_model["ports"]
        json_port_list_paths = [json_port["path"] for json_port in json_port_list]
        new_ports = list(set(ports) ^ set(json_port_list_paths))

        for new_port in new_ports:
            json_port_list.append(
                PortConfiguration(path=new_port, baud_rate=9600).model_dump()
            )
        modbus_model.config = json.dumps(json_modbus_model)
        await session.commit()
        json_modbus_configuration = json.loads(modbus_model.config)
        modbus_config = ModbusConfigurationCreate(**json_modbus_configuration)
        handle_list = [ModbusHandle(port) for port in modbus_config.ports]


async def load_tasks():
    global handle_list
    tasks = [asyncio.create_task(_.task_loop()) for _ in handle_list]
    try:
        await asyncio.gather(*tasks)
    except:
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_templates()
    await load_main_config()
    await load_serial_ports()
    await load_tasks()
    yield
