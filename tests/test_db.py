import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from oneorg.db.database import engine, get_db

@pytest.mark.asyncio
async def test_database_connection():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_get_db_yields_session():
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break
