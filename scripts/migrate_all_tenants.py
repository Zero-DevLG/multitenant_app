import asyncio
from app.core.database import get_control_db_session_standalone, control_engine
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.tenants.application.migration_runner import run_migrations
from app.tenants.domain.entities import TenantStatus
from app.core.utils import build_dsn

async def main():
    async with get_control_db_session_standalone() as session:
        repo = SqlAlchemyTenantRepository(session)
        tenants = await repo.list_by_status(TenantStatus.ACTIVE)

        for tenant in tenants:
            try:
                dsn = await build_dsn(tenant, tenant.secret_ref, async_driver=False)
                await asyncio.to_thread(run_migrations, tenant, dsn)
                print(f"OK: {tenant.db_name}")
            except Exception as e:
                print(f"FALLÓ: {tenant.db_name} -> {e}")
                
    await control_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())