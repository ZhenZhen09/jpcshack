import secrets
import string


def shift_text(text: str, shift: int) -> str:
    output = []
    for char in text:
        if char in string.ascii_uppercase:
            output.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char == " ":
            output.append("0")
        else:
            output.append(char)
    return "".join(output)


def create_state() -> dict:
    shift = secrets.randbelow(25) + 1
    flag = f"FLAG{{NET_SHIFT_{secrets.token_hex(4).upper()}}}"
    plain = f"THOUSAND CAESAR SHIFTS REDUCE TO ONE SHIFT. FLAG {flag}"
    return {"shift": shift, "flag": flag, "ciphertext": shift_text(plain, shift), "solved": False}


def public_state(state: dict) -> dict:
    return {"artifact": state["ciphertext"], "note": "Spaces were replaced with 0. The alphabet wraps from Z to A."}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    answer = payload.get("answer")
    if not isinstance(answer, str):
        return False, "Enter the recovered flag."
    if secrets.compare_digest(answer.strip().upper(), state["flag"]):
        return True, "Correct. The stacked shifts reduce to one net shift."
    return False, "Not quite. Try each net Caesar shift from 0 through 25."
