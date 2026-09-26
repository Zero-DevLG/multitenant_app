from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_control_db_session
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.business.operators.application.bulk_register_operator import BulkOperatorRegistrationService
from .schemas import BulkOperatorRegisterRequest, BulkOperatorRegisterResponse, OperatorRegisterResult

router = APIRouter(prefix="/operators")

async def get_bulk_operator_service(
    session: AsyncSession = Depends(get_control_db_session),
) -> BulkOperatorRegistrationService:
    control_repo = SqlAlchemyTenantRepository(session)
    return BulkOperatorRegistrationService(control_repo)

@router.post("/bulk-register", response_model=BulkOperatorRegisterResponse)
async def bulk_register_operator(
    data: BulkOperatorRegisterRequest,
    service: BulkOperatorRegistrationService = Depends(get_bulk_operator_service)
):
    results = await service.register_in_tenants(data)
    
    created = sum(1 for r in results if r["status"] == "created")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    return BulkOperatorRegisterResponse(
        total=len(results), created=created, skipped=skipped,
        failed=len(results) - created - skipped,
        results=[OperatorRegisterResult(**r) for r in results],
    )