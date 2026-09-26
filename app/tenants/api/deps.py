from fastapi import Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_control_db_session
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.tenants.infrastructure.tenant_resolver import tenant_resolver
from app.tenants.infrastructure.api_key_resolver import api_key_resolver
from app.tenants.infrastructure.engine_factory import engine_factory
from app.tenants.domain.entities import Tenant
from app.tenants.domain.exceptions import TenantNotFoundError, TenantNotActiveError, InvalidApiKeyError


async def get_current_tenant(
    request: Request,
    x_tenant_domain:str | None = Header(default=None, alias="X-Tenant-Domain"),
    x_tenant_api_key: str | None = Header(default=None, alias="X-Tenant-Api-Key"),
    control_session: AsyncSession = Depends(get_control_db_session),
) -> Tenant:
    repo = SqlAlchemyTenantRepository(control_session)
    
    try:
        if x_tenant_domain and x_tenant_api_key:
            # Usar AUTH API KEY
            return await api_key_resolver.resolve(x_tenant_domain, x_tenant_api_key, repo)
    
        host = request.headers.get("host", "").split(":")[0]
    
        if not host:
            raise HTTPException(status_code=400, detail="No se pudo determinal el domino del request")
    
        return await tenant_resolver.resolve(host, repo)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenantNotActiveError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidApiKeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    

async def get_tenant_db_session(
    tenant: Tenant = Depends(get_current_tenant),
) -> AsyncSession:
    sessionmaker = await engine_factory.get_sessionmaker(tenant)
    async with sessionmaker() as session:
        yield session