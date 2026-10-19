"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{LOGS_TELL_STORIES}'
ARTIFACT = 'web-07 access.log (UTC)\n03:16:58 10.0.2.4 GET /health 200 ua=monitor\n03:17:03 10.0.2.9 GET /assets/logo.svg 200 ua=browser\n03:17:19 10.0.2.9 GET /export?receipt=RkxBR3tMT0dTX1RFTExfU1RPUklFU30= 200 ua=curl/8.1\n03:17:25 10.0.2.4 GET /health 200 ua=monitor\n'
HINT = 'Filter around 03:17, inspect the unusual download query, and Base64-decode its value.'


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
