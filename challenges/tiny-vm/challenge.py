"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{TINY_VM_REVERSED}'
ARTIFACT = 'TinyVM instruction reference:\n0x10 LOAD_BUFFER; 0x22 XOR_EACH_BYTE <imm8>; 0x30 OUTPUT_ASCII; 0xFF HALT\n\nProgram:\n0000: 10\n0001: 22 37\n0003: 30\n0004: FF\n\nBuffer bytes (hex):\n71 7B 76 70 4C 63 7E 79 6E 68 61 7A 68 65 72 61 72 65 64 72 73 4A'
HINT = 'LOAD_BUFFER, XOR_EACH_BYTE 0x37, then OUTPUT_ASCII.'


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
