from app.business.verification.domain.exceptions import (
    VerificationModuleNotFoundError,
    SectionNotFoundError,
    FieldNotFoundError,
    InvalidFieldPayloadError
)

from app.business.verification.application.evaluate_status import CompositeStatusEvaluator

class BatchSaveFieldAnswerService:
    def __init__(self, session, single_service, rules_repo, answers_repo):
        self._session = session
        self._single_service = single_service
        self._rules_repo = rules_repo
        self._evaluator = CompositeStatusEvaluator(rules_repo, answers_repo)
        
    async def save_many(self, operator_id:int, items: list) -> dict:
        results = []
        touched_sections: set[tuple[str, str]] = set()
        
        for item in items:
            try:
                answer = await self._single_service.save(operator_id, item)
                await self._session.commit()
                results.append({
                    "field_code": item.field_code, "section": item.section, "status": "saved",
                    "answer_id": answer.id, "validation_state": answer.validation_state,
                })
                touched_sections.add((item.module, item.section))
            except (VerificationModuleNotFoundError, SectionNotFoundError, FieldNotFoundError, InvalidFieldPayloadError) as e: 
                await self._session.rollback()
                results.append({
                    "field_code": item.field_code, "section": item.section,
                    "status": "failed", "reason": str(e)
                })
        
        print(f"Toched: {touched_sections}")
        
        section_statuses = {}
        for module_name, section_name in touched_sections:
            module = await self._rules_repo.get_module_by_code(module_name)
            print(f"module: {module}")
            section = await self._rules_repo.get_section_by_code(module.id, section_name)
            section_statuses[section_name] = await self._evaluator.evaluate_section(operator_id, section.id)
            
        saved_count = sum(1 for r in results if r["status"] == "saved")
        return {
            "total": len(items), "saved": saved_count, "failed": len(items) - saved_count,
            "results": results, "section_statuses": section_statuses
        }