"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{FILE_CARVED}'
ARTIFACT = 'Raw disk hex excerpt (offset: bytes):\n0000: 4A 50 43 53 2D 44 49 53 4B 00 00 50 41 59 4C\n000F+00: 46 4C 41 47 7B 46 49 4C\n000F+08: 45 5F 43 41 52 56 45 44\n000F+10: 7D 00 45 4E 44\n\nMarker legend: ASCII 50 41 59 4C spells PAYL; bytes after it are the carved file.'
HINT = 'Locate the PAYL marker in the hex dump; the following bytes are the deleted text file.'


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
