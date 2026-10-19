"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{MASS_ASSIGNMENT}'
ARTIFACT = 'Synthetic profile API trace:\nPATCH /api/profile/17\nContent-Type: application/json\n{"display_name":"Mira","role":"admin","is_staff":true}\n\nResponse: 200\n{"id":17,"role":"admin","is_staff":true,"debug":"RkxBR3tNQVNTX0FTU0lHTk1FTlR9"}\nThe public form only exposes display_name; compare it with the accepted JSON fields.'
HINT = 'The server accepted is_staff from the JSON body. Decode the debug field returned by the privileged response.'


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
