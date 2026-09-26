from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from cachetools import LRUCache
from app.tenants.domain.entities import Tenant
from app.core.utils import build_dsn

class TenantEngineFactory:
    def __init__(self, max_cached_tenants: int = 100):
        self._cache = LRUCache(maxsize=max_cached_tenants)
        
    async def get_sessionmaker(self, tenant: Tenant) -> async_sessionmaker:
        if tenant.id not in self._cache:
            dsn = await build_dsn(tenant, tenant.secret_ref)
            engine = create_async_engine(dsn, pool_size=5, max_overflow=5, pool_pre_ping=True)
            self._cache[tenant.id] = async_sessionmaker(engine, expire_on_commit=False)
        return self._cache[tenant.id]
    
    async def dispose_all(self):
        for sessionmaker in self._cache.values():
            await sessionmaker.kw["bind"].dispose()
        self._cache.clear()

engine_factory = TenantEngineFactory()