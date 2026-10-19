import secrets


def create_state() -> dict:
    x, y, z = (secrets.randbelow(20) + 5 for _ in range(3))
    equations = [x**3 + z**2 + y, y**3 + x**2 + z, z**3 + y**2 + x, x + y + z]
    flag = f"flag{{candy_{secrets.token_hex(8)}}}"
    return {"x": x, "y": y, "z": z, "equations": equations, "flag": flag, "solved": False}


def public_state(state: dict) -> dict:
    a, b, c, total = state["equations"]
    return {"equations": [f"x^3 + z^2 + y = {a:,}", f"y^3 + x^2 + z = {b:,}", f"z^3 + y^2 + x = {c:,}", f"x + y + z = {total}"]}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    try:
        answers = tuple(int(payload[key]) for key in ("x", "y", "z"))
    except (KeyError, TypeError, ValueError):
        return False, "Enter positive whole numbers for x, y, and z."
    if any(value < 1 or value > 100 for value in answers):
        return False, "Each candy count must be between 1 and 100."
    if answers == (state["x"], state["y"], state["z"]):
        return True, f"Ledger balanced. Your flag: {state['flag']}"
    return False, "Those values do not satisfy all four equations."
