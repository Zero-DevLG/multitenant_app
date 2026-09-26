from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import control_engine
from app.tenants.infrastructure.engine_factory import engine_factory
from app.core.logging import get_logger


logger = get_logger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicación iniciando...")
    yield
    
    logger.info("Aplicación cerrando, liberando conexiones...")
    await engine_factory.dispose_all()
    await control_engine.dispose()
    logger.info("Conexiones liberadas. Apagado limpio.")