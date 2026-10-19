"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{IDOR_FOUND}'
ARTIFACT = 'Synthetic API trace (authenticated account: user_id=17)\nGET /api/tickets/7101 -> 200 {"owner_id":17,"subject":"printer","note":"replace toner"}\nGET /api/tickets/7102 -> 200 {"owner_id":22,"subject":"vpn","note":"reset requested"}\nGET /api/tickets/7103 -> 200 {"owner_id":31,"subject":"executive","recovery_blob":"RkxBR3tJRE9SX0ZPVU5EfQ=="}\nRoute source: ticket = tickets.get(ticket_id); return ticket  # ownership check absent'
HINT = 'The route checks that a record exists but never checks its owner. Inspect the out-of-scope ticket response.'


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
