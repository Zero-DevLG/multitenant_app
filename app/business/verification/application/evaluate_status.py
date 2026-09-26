from app.business.verification.domain.conditions import CONDITION_REGISTRY
from app.business.verification.domain.evaluation import EvaluationState, STATUS_LABEL_TO_STATE


def _apply_status_rules(children: list [dict], status_rules: list) -> str:
    for rule in status_rules:
        condition_fn = CONDITION_REGISTRY[rule.condition_name]
        if condition_fn(children):
            return rule.result_status
    return "Pending Completion"

class CompositeStatusEvaluator:
    def __init__(self, rules_repo, answers_repo):
        self._rules_repo = rules_repo
        self._answers_repo = answers_repo
        

    async def evaluate_section(self, operator_id:int, section_id: int) -> str:
        field_rules = await self._rules_repo.get_field_rules(section_id)
        answers = await self._answers_repo.get_answers_for_section(operator_id, section_id)
        print(f"answers: {answers}")
        answer_by_field_id = {a.section_field_rule_id: a for a in answers}
        print(f"answers_by_field: {answer_by_field_id}")
        
        children = []
        
        for rule in field_rules:
            answer = answer_by_field_id.get(rule.id)
            if answer is None:
                state = EvaluationState.INCOMPLETE
            elif answer.validation_state == "pending_verification":
                state = EvaluationState.PENDING_VERIFICATION
            elif answer.validation_state == "incorrect":
                state = EvaluationState.INCORRECT
            else:
                state = EvaluationState.VERIFIED
            children.append({"required": rule.required, "state": state})
            
        status_rules = await self._rules_repo.get_section_status_rules(section_id)
        return _apply_status_rules(children, status_rules)
    
    async def evaluate_module(self, operator_id: int, module_id: int) -> str:
        sections = await self._rules_repo.get_sections_by_module(module_id)
        
        children = []
        for section in sections:
            section_status = await self.evaluate_section(operator_id, section.id)
            children.append({
                "required": section.required,
                "state": STATUS_LABEL_TO_STATE[section_status],
            })
        status_rules = await self._rules_repo.get_module_status_rules(module_id)
        return _apply_status_rules(children, status_rules)