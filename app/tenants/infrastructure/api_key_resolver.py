import hashlib
import secrets as secrets_module
from cachetools import TTLCache
from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.entities import Tenant, TenantStatus
from app.tenants.domain.exceptions import (
    TenantNotFoundError,
    TenantNotActiveError,
    InvalidApiKeyError
)


class ApiKeyTenantResolver:
    def __init__(self, ttl_seconds: int = 60, maxsize: int = 500):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        
    async def resolve(self, domain: str, raw_api_key: str, repo: TenantRepository) -> Tenant:
        incoming_hash = hashlib.sha256(raw_api_key.encode()).hexdigest()
        cache_key = f"{domain}:{incoming_hash}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        record = await repo.get_api_key_by_domain(domain)
        if record is None:
            raise TenantNotFoundError(f"No hay ninguna API key activa registrada para el dominio: {domain}")
        
        if not secrets_module.compare_digest(incoming_hash, record.key_hash):
            raise ApiKeyTenantResolver(f"La API key proporcionada no es válida para este dominio")
        
        tenant = await repo.get_by_id(record.tenant_id)
        if tenant is None or tenant.status != TenantStatus.ACTIVE:
            raise TenantNotActiveError(f"El tenant asociado al dominio: {domain} no está activo")
        
        await repo.mark_api_key_used(record.id)
        
        self._cache[cache_key] = tenant
        return tenant


api_key_resolver = ApiKeyTenantResolver()