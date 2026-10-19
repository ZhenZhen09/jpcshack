"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{ELF_GATE_OPEN}'
ARTIFACT = 'ELF extract:\nArchitecture: x86-64\n0000000000401080 <print_secret>:\n  mov ecx, LENGTH\n  xor BYTE PTR [rdi+rcx], 0x5a\n  loop print_secret\n  call puts\n\nSection .rodata bytes:\n1C 16 1B 1D 21 1F 16 1C 05 1D 1B 0E 1F 05 15 0A 1F 14 27'
HINT = 'The loop XORs every .rodata byte with 0x5A. Apply that operation to the hex bytes.'


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
