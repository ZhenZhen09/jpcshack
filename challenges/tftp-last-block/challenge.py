"""Server-side fixed-answer validator for TFTP: The Last Block."""

import secrets


FLAG = "FLAG{TFTP_OBJECT_RECOVERED}"
PAYLOAD_NAME = "policy.bin"
XOR_KEY = "CROW"


def create_state() -> dict:
    # The answer is intentionally shared by every team. Only milestone progress
    # is session-specific.
    return {
        "flag": FLAG,
        "solved": False,
        "object_found": False,
        "key_found": False,
        "flag_submitted": False,
    }


def public_state(state: dict) -> dict:
    return {
        "object_found": bool(state.get("object_found")),
        "key_found": bool(state.get("key_found")),
        "solved": bool(state.get("solved")),
    }


def is_solved(state: dict) -> bool:
    return bool(state.get("object_found") and state.get("key_found") and state.get("flag_submitted"))


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    stage = payload.get("stage")
    answer = payload.get("answer")
    if not isinstance(answer, str):
        return False, "Enter an answer for this investigation step."

    answer = answer.strip()
    if stage == "object":
        if secrets.compare_digest(answer.casefold(), PAYLOAD_NAME):
            state["object_found"] = True
            return True, "Correct. The encrypted payload is identified."
        return False, "That object is a decoy. Check the transferred notes for the payload name."

    if stage == "key":
        if not state.get("object_found"):
            return False, "Identify the payload object before submitting its key."
        if secrets.compare_digest(answer.upper(), XOR_KEY):
            state["key_found"] = True
            return True, "Correct. Use this repeating key to recover the payload."
        return False, "That key does not match the clue in the second note."

    if stage == "flag":
        if not state.get("object_found") or not state.get("key_found"):
            return False, "Complete the object and key steps first."
        if secrets.compare_digest(answer.upper(), FLAG):
            state["flag_submitted"] = True
            return True, "Correct. You recovered the transferred flag."
        return False, "The recovered flag does not match. Recheck the XOR output."

    return False, "Unknown investigation step."
