# app/business/verification/application/answer_handlers.py
from app.business.verification.domain.exceptions import InvalidFieldPayloadError
from app.business.verification.infrastructure.file_storage import save_uploaded_file # MOdificarlo ya que el front lo enviara por ahora y despues de hara desde el back el sync con el storage
from app.business.verification.domain.reference_catalog import REFERENCE_CATALOG_COLUMN

async def handle_text(answers_repo, operator_id, field_rule, request):
    if request.value is None:
        raise InvalidFieldPayloadError(f"El campo '{field_rule.code}' requiere 'value' (es de tipo texto)")
    return await answers_repo.save_text_answer(operator_id, field_rule.id, request.value)


async def handle_file(answers_repo, operator_id, field_rule, request):
    print(request)
    if request.type_file_id is None:
        raise InvalidFieldPayloadError(
            f"El campo '{field_rule.code}' requiere 'type_file_id'"
        )
    #url = await save_uploaded_file(operator_id, field_rule.code, request.file_base64)
    return await answers_repo.save_file_answer(
        operator_id, field_rule.id, request.type_file_id, request.url, request.name,
    )


async def handle_address(answers_repo, operator_id, field_rule, request):
    if request.address is None:
        raise InvalidFieldPayloadError(f"El campo '{field_rule.code}' requiere 'address' (es de tipo domicilio)")
    return await answers_repo.save_address_answer(operator_id, field_rule.id, request.address.model_dump())

async def handle_catalog_reference(answers_repo, operator_id, field_rule, request):
    if request.catalog_id is None:
        raise InvalidFieldPayloadError(f"El campo: {field_rule.code} requiere catalog_id")
    column = REFERENCE_CATALOG_COLUMN[field_rule.type]
    return await answers_repo.save_catalog_reference_answer(operator_id, field_rule.id, column, request.catalog_id)


ANSWER_HANDLER_REGISTRY = {
    "text": handle_text,
    "file": handle_file,
    "address": handle_address,
    "authority_role": handle_catalog_reference,
    "entity_type": handle_catalog_reference,
    "business_activity": handle_catalog_reference,
}