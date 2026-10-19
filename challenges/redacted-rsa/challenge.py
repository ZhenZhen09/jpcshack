import math
import secrets


PRIMES = (263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499)
E = 17


def create_state() -> dict:
    while True:
        p, q = secrets.SystemRandom().sample(PRIMES, 2)
        phi = (p - 1) * (q - 1)
        if math.gcd(E, phi) == 1:
            break
    n = p * q
    flag = f"flag{{rsa_{secrets.token_hex(6)}}}"
    blocks = [pow(byte, E, n) for byte in flag.encode("ascii")]
    return {"p": p, "q": q, "n": n, "e": E, "blocks": blocks, "flag": flag, "solved": False}


def public_state(state: dict) -> dict:
    return {"n": state["n"], "e": state["e"], "blocks": state["blocks"]}


def check_answer(state: dict, payload: dict) -> tuple[bool, str]:
    try:
        p, q = int(payload["p"]), int(payload["q"])
    except (KeyError, TypeError, ValueError):
        return False, "Enter the two prime factors."
    if p * q == state["n"] and {p, q} == {state["p"], state["q"]}:
        return True, f"Recovered plaintext: {state['flag']}"
    return False, "Those factors do not match the public modulus."
