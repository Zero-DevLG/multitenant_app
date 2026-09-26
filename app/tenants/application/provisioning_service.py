from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.entities import TenantStatus, Tenant
from app.core.utils import slugify, build_dsn
from .db_provider import create_database
from .migration_runner import run_migrations
from app.tenants.domain.exceptions import (
    TenantNotFoundError,
    TenantAlreadyExistsError,
    InvalidTenantStatusError
)
from app.tenants.application.api_key_service import ApiKeyService

from app.core.utils import slugify, build_dsn
from .db_provider import create_database
from .migration_runner import run_migrations


class TenantProvisioningService:
    def __init__(
        self, 
        repo: TenantRepository,
        api_key_services: ApiKeyService
        ):
        self._repo = repo
        self._api_key_service = api_key_services
        
    async def request(self, company_name: str, domain: str, prefix: str ) -> Tenant:
        """Registra solicitud"""
        existing = await self._repo.get_by_domain(domain)
        if existing is not None:
            raise TenantAlreadyExistsError(f"Ya existe un tenant con el dominio '{domain}'")
        
        slug = slugify(company_name)
        return await self._repo.create(company_name, domain, f"tenant_{slug}", prefix)
    
    async def approve(self, tenant_id: str) -> Tenant:
        """Dispara el aprovisionamiento real. solo valida que siga en 'requested'."""
        tenant = await self._repo.get_by_id(tenant_id)
        print("OBTENIENDO TENANT")
        print(tenant)
        if tenant is None:
            raise TenantNotFoundError(f"No existe un tenant con id '{tenant_id}'")
        if tenant.status != TenantStatus.REQUESTED and tenant.status != TenantStatus.FAILED:
            raise InvalidTenantStatusError(
                f"No se puede aprobar un tenant en estado '{tenant.status}' (debe estar en 'requested')"
            )
            
        tenant = await self._repo.update_status(tenant.id, TenantStatus.APPROVED)
        
        print("SEGUNDO ESTADO TENANT")
        print(tenant)
        
        try:
            secret_ref = await create_database(tenant, self._repo)
            
            tenant = await self._repo.update_status(
                tenant.id, TenantStatus.PROVISIONING_DB_DONE, secret_ref=secret_ref
            )
            
            dsn_migraciones = await build_dsn(tenant, secret_ref, async_driver=False)
            run_migrations(tenant, dsn_migraciones)
            
            """Crear key de tenant"""
            await self._api_key_service.generate_api_key(
                tenant_id=tenant.id,
                domain=tenant.domain,
                name=f"Main Key for {tenant.name}"
            )
            
            tenant = await self._repo.update_status(tenant.id, TenantStatus.ACTIVE)
        except Exception as e:
            tenant = await self._repo.update_status(tenant.id, TenantStatus.FAILED, error=str(e))
            raise
        
      
        return tenant
    
    async def reject(self, tenant_id:str, reason: str | None = None) -> Tenant:
        """Cierra solicitud sin ejecutar cambios en infrastructura"""
        tenant = await self._repo.get_by_id(tenant_id)
        if tenant is None:
            raise TenantNotFoundError(f"No existe un tenant con id: '{tenant_id}'")
        if tenant.status != TenantStatus.REQUESTED:
            raise InvalidTenantStatusError(
                f"Nose puede rechazar un tenant en estado '{tenant.status}' (debe estar en 'requested')"
            )
        
        return await self._repo.update_status(tenant.id, TenantStatus.REJECTED, review_note=reason)
        
        
    async def supply(self, company_name: str, domain: str):
        slug = slugify(company_name)
        tenant = await self._repo.create(company_name, domain, f"tenant_{slug}")
        try:
            secret_ref = await create_database(tenant, self._repo)
            dsn_migraciones = await build_dsn(tenant, secret_ref, async_driver=False)
            run_migrations(tenant, dsn_migraciones)
            await self._repo.update_status(tenant.id, TenantStatus.ACTIVE)
        except Exception as e:
            await self._repo.update_status(tenant.id, TenantStatus.FAILED, error=str(e))
            raise
        return tenant