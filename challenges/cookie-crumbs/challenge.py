"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{COOKIE_CRUMB_ADMIN}'
ARTIFACT = 'staging.env backup:\nSESSION_HMAC_KEY=staging-cookie-key\n\nsession middleware: HS256; cookie format is header.payload.signature\nSet-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFnaW5nLWFkbWluIiwicm9sZSI6ImFkbWluIiwiZmxhZyI6IkZMQUd7Q09PS0lFX0NSVU1CX0FETUlOfSJ9.SFbryWQN05VRe6-9cc2DMyTU4yq7T4y2C_6jTIAUDd4; HttpOnly; SameSite=Lax\n\nTask: verify the signature with the recovered key, then inspect the claims.'
HINT = 'The token uses HS256. Recompute the HMAC with the supplied key, then Base64URL-decode the payload.'


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
