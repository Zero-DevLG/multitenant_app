from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_control_db_session
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.tenants.application.provisioning_service import TenantProvisioningService
from app.tenants.domain.entities import TenantStatus, Tenant
from app.tenants.domain.exceptions import (
    TenantAlreadyExistsError, TenantNotFoundError, InvalidTenantStatusError
)
from app.tenants.application.api_key_service import ApiKeyService

router = APIRouter(prefix="/admin/tenants")



async def get_api_key_service(
    session: AsyncSession = Depends(get_control_db_session),
) -> ApiKeyService:
    repo = SqlAlchemyTenantRepository(session)
    return ApiKeyService(repo)


async def get_provisioning_service(
    session: AsyncSession = Depends(get_control_db_session),
    api_key_service: ApiKeyService = Depends(get_api_key_service)
) -> TenantProvisioningService:
    repo = SqlAlchemyTenantRepository(session)
    return TenantProvisioningService(repo, api_key_service)

@router.post("/")
async def request_tenant(
    name: str, domain:str, prefix: str,
    service: TenantProvisioningService = Depends(get_provisioning_service),
):
    try:
        tenant = await service.request(name, domain, prefix)
    except TenantAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"id": tenant.id, "status": tenant.status}

@router.get("/pending")
async def list_pending_tenants(
    session: AsyncSession = Depends(get_control_db_session),
):
    repo = SqlAlchemyTenantRepository(session)
    tenants = await repo.list_by_status(TenantStatus.REQUESTED)
    return [{"id": t.id, "name": t.name, "domain": t.domain} for t in tenants] 

@router.post("/{tenant_id}/approve")
async def approve_tenant(
    tenant_id: str,
    service: AsyncSession = Depends(get_provisioning_service)
):
    try:
        tenant = await service.approve(tenant_id)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTenantStatusError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"id": tenant.id, "status": tenant.status}

@router.post("/{tenant_id}/reject")
async def reject_tenant(
    tenant_id: str, reason: str | None = None,
    service: TenantProvisioningService = Depends(get_provisioning_service)
):
    try:
        tenant = await service.reject(tenant_id, reason)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTenantStatusError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    return {"id": tenant.id, "status": tenant.status}

@router.post("/{tenant_id}/api-key")
async def generate_tenant_api_key(
    tenant_id:str,
    service: ApiKeyService = Depends(get_api_key_service),
):
    tenant = await service._repo.get_by_id(tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail=f"No existe un tenant con id: {tenant_id}")
    
    result = await service.generate_api_key(tenant_id, domain=tenant.domain)
    
    return result