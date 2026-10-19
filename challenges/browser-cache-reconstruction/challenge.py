"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{CACHE_REBUILT}'
ARTIFACT = 'cache-index.csv (same URL hash means same report):\nreport-part-02.cache,seq=02,body=UNIRV9SRU\nreport-part-04.cache,seq=04,body==\nreport-part-01.cache,seq=01,body=RkxBR3tDQ\nreport-part-03.cache,seq=03,body=JVSUxUfQ='
HINT = 'Use the report sequence numbers, join the Base64 fragments, then decode.'


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
