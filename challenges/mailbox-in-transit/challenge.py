"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{MAILBOX_ATTACHMENT}'
ARTIFACT = 'SMTP DATA excerpt — unrelated text parts omitted\nContent-Type: multipart/mixed; boundary=relay-77\n\n--relay-77\nContent-Type: text/plain; charset=utf-8\n\nPlease archive the attached delivery receipt.\n--relay-77\nContent-Type: application/octet-stream; name=receipt.txt\nContent-Transfer-Encoding: base64\n\nRkxBR3tNQUlMQk9YX0FUVEFDSE1FTlR9\n--relay-77--'
HINT = 'Find the application/octet-stream MIME part and Base64-decode its body.'


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
