from cachetools import TTLCache
from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.entities import Tenant, TenantStatus
from app.tenants.domain.exceptions import (
    TenantNotFoundError,
    TenantNotActiveError
)

class DomainTenantResolver:
    def __init__(self, ttl_seconds: int = 60, maxsize: int = 500):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        
    
    async def resolve(self, domain: str, repo: TenantRepository) -> Tenant:
        if domain in self._cache:
            return self._cache[domain]
        
        tenant = await repo.get_by_domain(domain)
        if tenant is None:
            raise TenantNotFoundError(f"No existe ningún tenant registrado para el dominio: {domain}")
        if tenant.status != TenantStatus.ACTIVE:
            raise TenantNotActiveError(
                f"El tenant del dominio: {domain} no está activo (estatus actual: {tenant.status})"
            )
        self._cache[domain] = tenant
        return tenant
    
tenant_resolver = DomainTenantResolver()