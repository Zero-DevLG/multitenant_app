from abc import ABC, abstractmethod
from .entities import Tenant, TenantStatus, KeyDomainTenant

class TenantRepository(ABC):
    @abstractmethod
    async def create(self, name: str, domain: str, db_name: str) -> Tenant: ...
    
    
    @abstractmethod
    async def get_by_domain(self, domain:str) -> Tenant | None: ...
    
    @abstractmethod
    async def get_by_name(self, name:str) -> Tenant | None: ...
    
    @abstractmethod
    async def get_by_id(self, tenant_id: str) -> Tenant | None: ...
    
    @abstractmethod
    async def update_status(
        self, tenant_id: str, status: TenantStatus, error: str | None = None,
        review_note: str | None = None, secret_ref:str | None = None,
    ) -> None: ...
    
    @abstractmethod
    async def list_assets(self) -> list[Tenant]: ...
    
    @abstractmethod
    async def create_api_key_domain(
        self, 
        tenant_id:str, domain: str, 
        key_prefix: str, 
        key_hash: str, 
        is_active: bool, 
        created_at: str, 
        name: str | None = None,
        last_used_at: str | None = None
    ) -> KeyDomainTenant: ...
    
    @abstractmethod
    async def get_api_key_by_domain(self, domain:str) -> None: ...
    
    @abstractmethod
    async def mark_api_key_used(self, api_key_id: str) -> None: ...
    
    