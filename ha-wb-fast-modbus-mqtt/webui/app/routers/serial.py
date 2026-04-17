from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.templates import templates


router = APIRouter(
    prefix="/serial",
    tags=["serial"]
)
