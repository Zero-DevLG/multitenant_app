from app.business.verification.domain.repository import VerificationRulesRepository, VerificationAnswersRepository
from app.business.verification.domain.exceptions import VerificationModuleNotFoundError, SectionNotFoundError, FieldNotFoundError
from app.business.verification.application.answer_handlers import ANSWER_HANDLER_REGISTRY
from app.business.verification.domain.entities import Answer


class SaveFieldAnswerService:
    def __init__(self, rules_repo: VerificationRulesRepository, answers_repo: VerificationAnswersRepository):
        self._rules_repo = rules_repo
        self._answers_repo = answers_repo

    async def save(self, operator_id: int, request) -> Answer:
        module = await self._rules_repo.get_module_by_code(request.module)
        if module is None:
            raise VerificationModuleNotFoundError(f"No existe el módulo '{request.module}'")

        section = await self._rules_repo.get_section_by_code(module.id, request.section)
        if section is None:
            raise SectionNotFoundError(f"No existe la sección '{request.section}' en el módulo '{request.module}'")

        field_rule = await self._rules_repo.get_field_rule_by_code(section.id, request.field_code)
        if field_rule is None:
            raise FieldNotFoundError(f"El campo '{request.field_code}' no existe (o está inactivo) en '{request.section}'")

        handler = ANSWER_HANDLER_REGISTRY[field_rule.type]
        return await handler(self._answers_repo, operator_id, field_rule, request)