import asyncio 
import argparse
from app.core.database import get_control_db_session_standalone, control_engine
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.tenants.infrastructure.engine_factory import engine_factory
from app.tenants.domain.entities import TenantStatus
from app.seeders.registry import SEEDER_REGISTRY


# Catalogo de seeders
import app.seeders.default_catalogs
import app.seeders.default_section_catalog
import app.seeders.default_catalog_addresses_types

async def main(seeder_name:str, domains: list[str] | None):
    seeders_cls = SEEDER_REGISTRY.get(seeder_name)
    
    if seeders_cls is None:
        print(f"No existe un seeder llamado: {seeder_name}. Disponibles: {list(SEEDER_REGISTRY.keys())}")
        
        return
    
    seeder = seeders_cls()
    
    async with get_control_db_session_standalone() as control_session:
        repo = SqlAlchemyTenantRepository(control_session)
        
        if domains:
            tenants = []
            for domain in domains:
                tenant = await repo.get_by_domain(domain)
                if tenant is None:
                    print(f"AVISO no existe un tenant con dominio: {domain}, se omite")
                    continue
                tenants.append(tenant)
        else:
            tenants = await repo.list_by_status(TenantStatus.ACTIVE)
            
    for tenant in tenants:
        try:
            sessionmaker = await engine_factory.get_sessionmaker(tenant)
            async with sessionmaker() as session:
                await seeder.run(session)
            print(f"OK: {tenant.domain}")
        except Exception as e:
            print(f"FALLO: {tenant.domain} -> {e}")
            
    await control_engine.dispose()
    await engine_factory.dispose_all()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corre un seeder sobre uno o varios tenants")
    parser.add_argument("--seeder", required=True, help="Nombre del seeder a ejecutar")
    parser.add_argument("--domains", help="Dominios separados por coma. Si se omite , corre TODOS los tenants activos")
    
    args = parser.parse_args()
    
    domains = args.domains.split(",") if args.domains else None
    asyncio.run(main(args.seeder, domains))


