"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{POLICY_DIFF_FOUND}'
ARTIFACT = 'old policy.conf:\nlocation /internal/backup { allow 127.0.0.1; deny all; }\n\ncurrent policy.conf:\nlocation /internal/backup { allow all; }\n\naccess.log:\n10.0.4.5 GET /internal/health 200\n10.0.4.5 GET /internal/backup 200 body=RkxBR3tQT0xJQ1lfRElGRl9GT1VORH0=\n'
HINT = 'The new public location is /internal/backup. Its response body is Base64 encoded.'


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
