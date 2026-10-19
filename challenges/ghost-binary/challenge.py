import secrets


def create_state() -> dict:
    key = secrets.randbelow(256)
    flag = f"flag{{xor_reverse_{secrets.token_hex(6)}}}"
    artifact = bytes(value ^ key for value in flag.encode("ascii")).hex()
    return {"key": key, "flag": flag, "artifact": artifact, "solved": False}


def public_state(state: dict) -> dict:
    return {"artifact": state["artifact"]}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    key = payload.get("key")
    if not isinstance(key, str) or len(key) != 2:
        return False, "Enter one hexadecimal byte from 00 to ff."
    try:
        value = int(key, 16)
    except ValueError:
        return False, "Enter one hexadecimal byte from 00 to ff."
    if value == state["key"]:
        return True, f"Decoded firmware: {state['flag']}"
    return False, "That key did not produce the flag. Try a different byte."
