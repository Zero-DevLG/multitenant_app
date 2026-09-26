# app/business/verification/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenants.api.deps import get_tenant_db_session
from app.business.users.api.deps import get_current_user_and_operator
from app.business.operators.domain.entities import Operator
from app.business.verification.infrastructure.repository_sqlalchemy import (
    SqlAlchemyVerificationRuleRepository,
    SqlAlchemyVerificationAnswersRepository
)
from app.business.verification.application.save_field_answer import SaveFieldAnswerService
from app.business.verification.application.evaluate_status import CompositeStatusEvaluator
from app.business.verification.domain.exceptions import (
    VerificationModuleNotFoundError, SectionNotFoundError, FieldNotFoundError, InvalidFieldPayloadError,
)
from app.business.verification.application.build_operator_overview import BuildOperatorOverviewService
from .schemas import SaveFieldAnswerRequest, SaveFieldAnswerResponse, SavedFieldAnswersBatchResponse, SaveFieldAnswersBatchRequest
from app.business.verification.api.schemas import OperatorOverviewResponse, OverviewRequest

from app.business.verification.application.batch_save_field_answers import BatchSaveFieldAnswerService

router = APIRouter(prefix="/verification", tags=["verification"])


@router.get("/get_modules")
async def get_modules(
    session: AsyncSession = Depends(get_tenant_db_session)
):
   
    rules_repo = SqlAlchemyVerificationRuleRepository(session)
    data = await rules_repo.get_all_modules()
    return {
        "status": 200,
        "data": data
    }

@router.get("/get_module_sections/{module_id}")
async def get_module_sections(
    module_id: int,
    session: AsyncSession = Depends(get_tenant_db_session)
):
    rules_repo = SqlAlchemyVerificationRuleRepository(session)
    data = await rules_repo.get_sections_by_module(module_id)
    return {
        "status": 200,
        "data": data
    }

    
@router.post("/post_overview")
async def get_operator_overview(
    payload: OverviewRequest,
    operator: Operator = Depends(get_current_user_and_operator),
    session: AsyncSession = Depends(get_tenant_db_session),
):
    print(f"datos: {payload.module_id}, {payload.section_id}")
    rules_repo =SqlAlchemyVerificationRuleRepository(session)
    answers_repo = SqlAlchemyVerificationAnswersRepository(session)
    service = BuildOperatorOverviewService(rules_repo, answers_repo)
    
   
    data_raw = await service.build(operator.id, payload.module_id, payload.section_id)
    
    #data = OperatorOverviewResponse(**data_raw)
    
    return {
        "status": 200,
        "data": data_raw
    }



@router.post("/answers", response_model=SaveFieldAnswerResponse)
async def save_field_answer(
    data: SaveFieldAnswerRequest,
    operator: Operator = Depends(get_current_user_and_operator),
    session: AsyncSession = Depends(get_tenant_db_session),
):
    rules_repo = SqlAlchemyVerificationRuleRepository(session)
    answers_repo = SqlAlchemyVerificationAnswersRepository(session)
    service = SaveFieldAnswerService(rules_repo, answers_repo)

    try:
        answer = await service.save(operator.id, data)
        await session.commit()
    except (VerificationModuleNotFoundError, SectionNotFoundError, FieldNotFoundError) as e:
        await session.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidFieldPayloadError as e:
        await session.rollback()
        raise HTTPException(status_code=422, detail=str(e))

    #
    module = await rules_repo.get_module_by_code(data.module)
    section = await rules_repo.get_section_by_code(module.id, data.section)
    evaluator = CompositeStatusEvaluator(rules_repo, answers_repo)
    section_status = await evaluator.evaluate_section(operator.id, section.id)

    return SaveFieldAnswerResponse(
        answer_id=answer.id, field_code=data.field_code,
        validation_state=answer.validation_state, section_status=section_status,
    )
    
    
@router.post("/post_answers/batch", response_model=dict)
async def save_field_answers_batch(
    data: SaveFieldAnswersBatchRequest,
    operator: Operator = Depends(get_current_user_and_operator),
    session: AsyncSession = Depends(get_tenant_db_session),
):
    rules_repo = SqlAlchemyVerificationRuleRepository(session)
    answers_repo = SqlAlchemyVerificationAnswersRepository(session)
    single_service = SaveFieldAnswerService(rules_repo, answers_repo)
    batch_service = BatchSaveFieldAnswerService(session, single_service, rules_repo, answers_repo)
    
    result = await batch_service.save_many(operator.id, data.answers)
    data_response = SavedFieldAnswersBatchResponse(**result)
    
    return {
        "status": 200,
        "data": data_response
    }
    
@router.get("/status")
async def get_section_status(
    module: str, section: str,
    operator: Operator = Depends(get_current_user_and_operator),
    session: AsyncSession = Depends(get_tenant_db_session),
):
    rules_repo = SqlAlchemyVerificationRuleRepository(session)
    answers_repo = SqlAlchemyVerificationAnswersRepository(session)

    mod = await rules_repo.get_module_by_code(module)
    if mod is None:
        raise HTTPException(status_code=404, detail=f"No existe el módulo '{module}'")
    sec = await rules_repo.get_section_by_code(mod.id, section)
    if sec is None:
        raise HTTPException(status_code=404, detail=f"No existe la sección '{section}'")

    evaluator = CompositeStatusEvaluator(rules_repo, answers_repo)
    status = await evaluator.evaluate_section(operator.id, sec.id)
    return {"module": module, "section": section, "status": status}