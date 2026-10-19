import secrets
import string


CANDIDATES = ("sunshine", "password1", "candyshop", "pumpkin5", "redballoon", "winter2025", "secretkey", "coffee42")


def encrypt(plain: str, key: str) -> str:
    output = []
    index = 0
    for char in plain:
        if char in string.ascii_lowercase:
            shift = ord(key[index % len(key)].lower()) - 97
            output.append(chr((ord(char) - 97 + shift) % 26 + 97))
            index += 1
        else:
            output.append(char)
    return "".join(output)


def create_state() -> dict:
    key = secrets.choice(CANDIDATES)
    flag = f"flag{{dictionary_{secrets.token_hex(6)}}}"
    return {"key": key, "flag": flag, "ciphertext": encrypt(flag, key), "candidates": list(CANDIDATES), "solved": False}


def public_state(state: dict) -> dict:
    return {"artifact": state["ciphertext"], "candidates": state["candidates"]}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    password = payload.get("password")
    if not isinstance(password, str):
        return False, "Enter one of the candidate passwords."
    if secrets.compare_digest(password.strip().lower(), state["key"]):
        return True, f"Password found. Decrypted flag: {state['flag']}"
    return False, "That candidate did not produce a flag. Try the next entry."
