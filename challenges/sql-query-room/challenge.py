"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{UNSAFE_QUERY}'
ARTIFACT = "Synthetic query audit (no live database)\nInput: ' OR 1=1 --\nQuery: SELECT username,recovery_blob FROM users WHERE username='' OR 1=1 --'\nReturned rows:\nalice | ordinary\nbob | disabled\nservice_backup | RkxBR3tVTlNBRkVfUVVFUll9\n"
HINT = 'The query condition is always true. Find the recovery_blob in the returned result and Base64-decode it.'


def create_state() -> dict:
    return {"flag": FLAG, "solved": False}


def public_state(state: dict) -> dict:
    return {"artifact": ARTIFACT, "hint": HINT}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    answer = payload.get("answer")
    if not isinstance(answer, str):
        return False, "Submit the recovered flag as text."
    if secrets.compare_digest(answer.strip().upper(), FLAG):
        return True, "Correct. Flag accepted."
    return False, "Not yet. Recheck the artifact and apply the hint."
