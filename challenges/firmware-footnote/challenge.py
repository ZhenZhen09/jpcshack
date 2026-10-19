"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{FIRMWARE_FOOTNOTE}'
ARTIFACT = 'JPCS-FW image header\nmagic: 4A 50 43 53\nversion: 01\npayload_offset: 0x10\nconfig_xor_key: 0x2A\npayload_size: 23\n\nimage bytes at payload_offset (hex):\n6C 66 6B 6D 51 6C 63 78 67 7D 6B 78 6F 75 6C 65 65 7E 64 65 7E 6F 57'
HINT = "The payload starts at offset 0x10. XOR each byte with the header's key 0x2A."


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
