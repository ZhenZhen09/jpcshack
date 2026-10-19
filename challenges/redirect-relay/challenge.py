"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{REDIRECT_CHAIN}'
ARTIFACT = 'HTTP redirect trace:\nGET /go?next=/relay -> 302 Location: /relay?state=unchanged\nGET /relay?state=unchanged -> 302 Location: /finish?state=FLAG%257BREDIRECT_CHAIN%257D\nGET /finish?state=<value> -> 200 archived status page\nThe state parameter was URL-encoded twice by two proxy hops.'
HINT = 'Follow each Location value and URL-decode the final state twice.'


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
