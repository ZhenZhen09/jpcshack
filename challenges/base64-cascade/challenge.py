import base64
import secrets


def create_state() -> dict:
    flag = f"zeroday{{{secrets.token_hex(12)}}}"
    encoded = base64.b64encode(base64.b64encode(flag.encode("ascii"))).decode("ascii")
    return {"flag": flag, "artifact": encoded, "solved": False}


def public_state(state: dict) -> dict:
    return {"artifact": state["artifact"]}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    answer = payload.get("answer")
    if not isinstance(answer, str):
        return False, "Enter the recovered flag."
    if secrets.compare_digest(answer.strip(), state["flag"]):
        return True, "Correct. The note had two Base64 layers."
    return False, "Not yet. Decode the first result one more time."
