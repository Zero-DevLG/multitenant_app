import re
from app.core.config import settings
from app.core.secrets import get_secret
from app.tenants.domain.entities import Tenant

def slugify(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")

async def build_dsn(tenant: Tenant, secret_ref: str, async_driver: bool = True) -> str:
    """
    async_driver=True  -> para el uso normal de negocio (engine_factory, consultas async)
    async_driver=False -> para Alembic, que corre de forma síncrona
    """
    
    password = await get_secret(secret_ref)
    driver = "mysql+aiomysql" if async_driver else "mysql+pymysql"
    return (
        f"{driver}://{tenant.db_name}_user:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{tenant.db_name}"
    )