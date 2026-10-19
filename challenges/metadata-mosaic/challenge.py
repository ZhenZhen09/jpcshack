"""Fixed-answer challenge data and validator. The same flag applies to every team."""

import secrets


FLAG = 'FLAG{METADATA_MOSAIC}'
ARTIFACT = 'Synthetic EXIF inventory:\nimg_03.jpg | DateTimeOriginal=2026:10:18 09:42:11 | ImageDescription=AIC}\nimg_01.jpg | DateTimeOriginal=2026:10:18 09:41:02 | ImageDescription=FLAG{MET\nimg_02.jpg | DateTimeOriginal=2026:10:18 09:41:37 | ImageDescription=ADATA_MOS\ndecoy.jpg | DateTimeOriginal=2026:10:18 09:40:00 | ImageDescription=ordinary conference photo'
HINT = 'Sort by DateTimeOriginal and join the ImageDescription fragments.'


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
