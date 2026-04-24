import pytest
import pytest_asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db_depends import get_async_db
from app.database import Base
from app.main import app
import os


@pytest_asyncio.fixture(scope="function")
async def get_async_db_test(tmp_path: Path):
    db_file = tmp_path / "test.db"
    async_engine = create_async_engine(f"sqlite+aiosqlite:///{str(db_file)}", echo=False)
    async_session = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_async_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_async_db] = override_get_async_db

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await async_engine.dispose()
        if db_file.exists():
            db_file.unlink()
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(tmp_path: Path, get_async_db_test):
    tmp_file_path = tmp_path / "options.json"
    data = {
        "Serial port config": [
            {"Port": "/dev/ttyRS485-1"},
            {"Port": "/dev/ttyRS485-2"},
        ]
    }
    tmp_file_path.write_text(json.dumps(data), encoding="utf-8")
    os.environ["PATH_TO_OPTIONS"] = str(tmp_file_path)
    with TestClient(app, "http://test") as test_client:
        yield test_client
