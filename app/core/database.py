from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from app.core.config import settings

ControlBase = declarative_base()
BusinessBase = declarative_base()

control_engine = create_async_engine(settings.CONTROL_DB_DSN, pool_pre_ping=True)
ControlSessionLocal = async_sessionmaker(control_engine, expire_on_commit=False)

async def get_control_db_session() -> AsyncSession:
    async with ControlSessionLocal() as session:
        yield session
        

@asynccontextmanager
async def get_control_db_session_standalone():
    async with ControlSessionLocal() as session:
        yield session
