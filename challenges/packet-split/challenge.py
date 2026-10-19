"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{TCP_SEGMENTS_REBUILT}'
ARTIFACT = 'TCP stream fragment log (sequence numbers are relative):\nseq=0x18A0 payload==\nseq=0x1880 payload=VUlMVH0\nseq=0x1860 payload=FNfUkVC\nseq=0x1840 payload=VHTUVOV\nseq=0x1820 payload=UQ1BfU0\nseq=0x1800 payload=RkxBR3t'
HINT = 'Sort the payloads by TCP sequence number, concatenate them, and Base64-decode.'


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
