"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{USB_TYPER}'
ARTIFACT = 'USB HID boot-keyboard reports: modifier, usage (00 00 marks release)\n02 09\n02 0F\n02 04\n02 0A\n02 2F\n02 18\n02 16\n02 05\n02 2D\n02 17\n02 1C\n02 13\n02 08\n02 15\n02 30\n\nUsage map: A-Z = 04-1D; 1-9 = 1E-26; 0 = 27.\nPunctuation: - = 2D, [ = 2F, ] = 30; Shift (modifier 02) makes _, {, }.'
HINT = 'Modifier 0x02 means Shift. Letter usages start at A=0x04; the artifact includes the number and punctuation mapping.'


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
