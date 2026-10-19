"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{GIT_REMEMBERS}'
ARTIFACT = 'git log --oneline --all\nc81a92b remove temporary debug setting\n22c7b01 add startup configuration\n\ngit show c81a92b -- config/debug.env\ndiff --git a/config/debug.env b/config/debug.env\n-DEBUG_ARCHIVE_TOKEN=FLAG{GIT_REMEMBERS}\n+DEBUG_ARCHIVE_TOKEN=removed\n'
HINT = 'The newest commit deletes a debug setting. Read the removed line in the patch.'


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
