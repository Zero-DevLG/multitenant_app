from enum import Enum

class EvaluationState(str, Enum):
    INCOMPLETE = "incomplete"
    PENDING_VERIFICATION = "pending_verification"
    INCORRECT = "incorrect"
    VERIFIED = "verified"
    
    
STATUS_LABEL_TO_STATE = {
    "Pending Completion" : EvaluationState.INCOMPLETE,
    "Pending Verification": EvaluationState.PENDING_VERIFICATION,
    "Requires Correction": EvaluationState.INCORRECT,
    "Verified": EvaluationState.VERIFIED
}