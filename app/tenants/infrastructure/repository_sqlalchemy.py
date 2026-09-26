from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.entities import Tenant, TenantStatus, KeyDomainTenant, ApiKeyRecord
from .models import TenantModel, DomainApiKeyModel
from datetime import datetime, timezone
import uuid



def _to_entity(model: TenantModel) -> Tenant:
    return Tenant(
        id=model.id,
        name=model.name,
        domain=model.domain,
        db_name=model.db_name,
        status=model.status,
        secret_ref=model.secret_ref,
        error=model.error,
        review_note=model.review_note,
        prefix=model.prefix
    )

def _to_entity_Key(model:DomainApiKeyModel) -> KeyDomainTenant:
    return KeyDomainTenant(
        id=model.id,
        name=model.name,
        key=f"{model.key_prefix}_{model.key_hash}",
        created_at=model.created_at
    )
    
def _api_key_to_entity(model: DomainApiKeyModel) -> ApiKeyRecord:
    return ApiKeyRecord(
        id=model.id, tenant_id=model.tenant_id, domain=model.domain,
        key_prefix=model.key_prefix, key_hash=model.key_hash,
        is_active=model.is_active, last_used_at=model.last_used_at,
    )
    
class SqlAlchemyTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def create(self, name: str, domain: str, db_name: str, prefix:str) -> Tenant:
        model = TenantModel(
            id=str(uuid.uuid4()), name = name, domain = domain,
            db_name=db_name, status=TenantStatus.REQUESTED, prefix=prefix
        )
        
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
    
    async def create_api_key_domain(self, tenant_id, domain, key_prefix, key_hash, is_active, created_at, name = None, last_used_at = None):
        model = DomainApiKeyModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            domain=domain,
            key_prefix=key_prefix,
            key_hash=key_hash,
            is_active=is_active,
            created_at=created_at,
            last_used_at=None
        )
        
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity_Key(model)
    
    async def get_api_key_by_domain(self, domain: str) -> ApiKeyRecord | None:
        result = await self._session.execute(
            select(DomainApiKeyModel).where(
                DomainApiKeyModel.domain == domain,
                DomainApiKeyModel.is_active == True,
            )
        )
        
        model = result.scalar_one_or_none()
        
        return _api_key_to_entity(model) if model else None
    
    async def mark_api_key_used(self, api_key_id):
        model = await self._session.get(DomainApiKeyModel, api_key_id)
        if model:
            model.last_used_at = datetime.now(timezone.utc)
            await self._session.commit()
    
    async def get_by_domain(self, domain: str) -> ApiKeyRecord | None:
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.domain == domain)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
    
    
    async def get_by_name(self, name):
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.name == name)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
    
    
    async def get_by_id(self, tenant_id: str) -> None:
        model = await self._session.get(TenantModel, tenant_id)
        return _to_entity(model) if model else None
    
    
    
    async def update_status(self, tenant_id, status, error = None, review_note = None, secret_ref= None) -> Tenant:
        model = await self._session.get(TenantModel, tenant_id)
        model.status = status
        model.error = error
        if review_note is not None:
            model.review_note = review_note
        if secret_ref is not None:
            model.secret_ref = secret_ref
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
        
    async def list_assets(self) -> list[Tenant]:
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.status == TenantStatus.ACTIVE)
        )
        return [_to_entity(m) for m in result.scalars()]
    
    async def list_by_status(self, status: TenantStatus) -> list[Tenant]:
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.status == status)
        )
        return [_to_entity(m) for m in result.scalars()]
    
 