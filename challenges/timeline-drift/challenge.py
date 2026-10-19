"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{TIMELINE_NORMALIZED}'
ARTIFACT = 'event fragments (normalize to UTC; date is the same for this exercise):\n2026-10-18T05:08:00-05:00 fragment=JFNEKRD5\n2026-10-18T12:06:00+02:00 fragment=J5JE2QKM\n2026-10-18T10:04:00+00:00 fragment=JFHEKX2O\n2026-10-18T05:02:00-05:00 fragment=KREU2RKM\n2026-10-18T12:00:00+02:00 fragment=IZGECR33'
HINT = 'Convert each timestamp to UTC, order the events, join the fragments, then Base32-decode.'


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
