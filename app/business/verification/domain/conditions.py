from app.business.verification.domain.evaluation import EvaluationState

def any_required_missing(children: list[dict]) -> bool:
    return any(c["required"] and c["state"] == EvaluationState.INCOMPLETE for c in children)

def any_required_pending_verification(children: list[dict]) -> bool:
    return any(c["required"] and c["state"] == EvaluationState.PENDING_VERIFICATION for c in children)

def any_required_incorrect(children: list[dict]) -> bool:
    return any(c["required"] and c["state"] == EvaluationState.INCORRECT for c in children)

def all_required_correct(children: list[dict]) -> bool:
    return any(c["state"] == EvaluationState.VERIFIED for c in children if c["required"])

CONDITION_REGISTRY = {
    "any_required_missing": any_required_missing,
    "any_required_pending_verification": any_required_pending_verification,
    "any_required_incorrect": any_required_incorrect,
    "all_required_correct": all_required_correct
}