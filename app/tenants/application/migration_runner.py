from alembic.config import Config
from alembic import command
from app.tenants.domain.entities import Tenant

def run_migrations(tenant: Tenant, dsn: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(alembic_cfg, "head")