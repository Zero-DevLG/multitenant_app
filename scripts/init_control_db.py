import asyncio
from app.core.database import control_engine, ControlBase
from app.tenants.infrastructure.models import TenantModel 


async def main():
    async with control_engine.begin() as conn:
        await conn.run_sync(ControlBase.metadata.create_all)
    print("Tabla 'tenants' creada en control_db")
    
if __name__ == "__main__":
    asyncio.run(main())