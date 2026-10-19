"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{HEADER_HUNT_COMPLETE}'
ARTIFACT = 'HTTP/1.1 302 Found\nServer: archive-proxy\nX-Fallback: /backup/rollout.old\nLocation: /status\n\nGET /backup/rollout.old\nHTTP/1.1 200 OK\nContent-Type: text/plain\nX-Recovery-Field: token\n\ntoken=FLAG%7BHEADER_HUNT_COMPLETE%7D\n'
HINT = 'The X-Fallback header names the backup route. URL-decode its recovery parameter.'


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
