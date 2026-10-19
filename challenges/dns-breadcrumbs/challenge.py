"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{DNS_BREADCRUMBS}'
ARTIFACT = 'Resolver query export (fragment index is authoritative):\n03:22:00.0  client=10.8.0.14  qname=05-PU.vault.corp.test\n03:22:01.0  client=10.8.0.14  qname=04-KJKU2QST.vault.corp.test\n03:22:02.0  client=10.8.0.14  qname=03-KJCUCRCD.vault.corp.test\n03:22:03.0  client=10.8.0.14  qname=02-IRHFGX2C.vault.corp.test\n03:22:04.0  client=10.8.0.14  qname=01-IZGECR33.vault.corp.test'
HINT = 'Sort fragments by their sequence number, join them, restore Base32 padding, then decode.'


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
