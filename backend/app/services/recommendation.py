"""The suggested call is a fixed policy. An optional language model may phrase the brief, not choose the call."""

from app.services.retrieval import families_in

SAFETY_CODES = {"E900", "E910", "ESTOP", "E-STOP", "GUARD"}
SAFETY_LINE = "This is a recommendation. An authorized person decides. This does not change the line."


def is_safety(error_code: str | None, symptom: str, observation: str) -> bool:
    code = (error_code or "").strip().upper()
    if code in SAFETY_CODES:
        return True
    blob = f"{symptom} {observation}".lower()
    if "e-stop" in blob or "estop" in blob:
        return True
    return "safety" in families_in(symptom, observation)


def repair_successful(outcome: str | None) -> bool:
    if not outcome:
        return False
    text = outcome.lower()
    return "returned to normal" in text or "resolved" in text


def recommend(*, top_score: float | None, top_successful: bool, safety: bool) -> str:
    if safety:
        return "stop"
    if top_score is not None and top_score >= 0.80 and top_successful:
        return "slow"
    return "continue"
