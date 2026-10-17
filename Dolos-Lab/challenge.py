"""Deterministic Dolos challenge logic and the fixed simulated tool."""

from __future__ import annotations

import re


FLAG = "THM{dolos_diagnostic_is_simulated}"
FINAL_STAGE = 3
SOLVED_STAGE = 4

GUIDANCE = (
    {
        "title": "Find the deployment record",
        "hint": "I can only share records marked for the release review. One deployment summary was cleared for visitors.",
    },
    {
        "title": "Inspect the archive index",
        "hint": "The public summary points to the maintenance archive. Its index explains how the records are grouped.",
    },
    {
        "title": "Read the diagnostic policy",
        "hint": "The archive index mentions a diagnostic report. Look for the policy attached to that record.",
    },
    {
        "title": "Challenge the assistant's instructions",
        "hint": "The report is restricted by the assistant's instructions. Check whether those instructions are the same as a real access control.",
    },
    {
        "title": "Investigation complete",
        "hint": "The simulated report is available again if you need to copy the flag.",
    },
)

CLUES = (
    "Deployment summary: the public chat service uses the standard assistant profile. "
    "Maintenance records are kept in the internal archive.",
    "Archive index: the calibration report is listed with the diagnostic records. "
    "The index points to the policy attached to that report.",
    "Diagnostic policy: the assistant is instructed to keep the calibration report private "
    "and to refuse ordinary requests for it.",
)

_INJECTION_PATTERNS = (
    re.compile(r"\bignore\b.{0,50}\b(instruction|rule|policy)s?\b", re.I),
    re.compile(r"\bforget\b.{0,50}\b(instruction|rule|policy)s?\b", re.I),
    re.compile(r"\boverride\b.{0,50}\b(instruction|rule|policy)s?\b", re.I),
    re.compile(r"\b(disregard|bypass)\b.{0,50}\b(instruction|rule|policy)s?\b", re.I),
)


def new_state() -> dict:
    """Create a fresh per-browser challenge state."""
    return {"stage": 0, "solved": False}


def _stage(state: dict) -> int:
    try:
        value = state.get("stage", 0)
        return value if type(value) is int and 0 <= value <= SOLVED_STAGE else 0
    except AttributeError:
        return 0


def _response(stage: int, reply: str, solved: bool = False) -> dict:
    return {
        "reply": reply,
        "solved": solved,
        "guidance": dict(GUIDANCE[min(stage, SOLVED_STAGE)]),
    }


def _contains_all(message: str, *terms: str) -> bool:
    words = set(re.findall(r"[a-z0-9]+", message.casefold()))
    return all(term in words for term in terms)


def _is_prompt_injection(message: str) -> bool:
    return any(pattern.search(message) for pattern in _INJECTION_PATTERNS)


def handle_local_message(state: dict, message: str) -> tuple[dict, dict]:
    """Advance known puzzle actions, or simulate an injected tool request."""
    updated = dict(state) if isinstance(state, dict) else new_state()
    stage = _stage(updated)
    updated["stage"] = stage
    updated["solved"] = bool(updated.get("solved", False))
    normalized = " ".join(message.casefold().split())

    if stage == 0 and "deployment" in normalized and any(
        marker in normalized for marker in ("public", "summary", "record")
    ):
        updated["stage"] = 1
        return updated, _response(1, CLUES[0])

    if stage == 1 and "archive" in normalized and any(
        marker in normalized for marker in ("index", "organize", "organise", "maintenance")
    ):
        updated["stage"] = 2
        return updated, _response(2, CLUES[1])

    if stage == 2 and "diagnostic" in normalized and any(
        marker in normalized for marker in ("policy", "report", "rule")
    ):
        updated["stage"] = FINAL_STAGE
        return updated, _response(FINAL_STAGE, CLUES[2])

    if stage == FINAL_STAGE and _is_prompt_injection(message):
        return accept_tool_request(updated, "read_diagnostic", {})

    if stage >= SOLVED_STAGE and _is_prompt_injection(message):
        return accept_tool_request(updated, "read_diagnostic", {})

    return updated, _response(stage, "I can't help with that request yet.")


def accept_tool_request(state: dict, tool_name: str, arguments: object) -> tuple[dict, dict]:
    """Execute the single simulated, argument-free diagnostic lookup."""
    updated = dict(state) if isinstance(state, dict) else new_state()
    stage = _stage(updated)
    updated["stage"] = stage
    updated["solved"] = bool(updated.get("solved", False))

    if (
        tool_name == "read_diagnostic"
        and type(arguments) is dict
        and not arguments
        and stage in (FINAL_STAGE, SOLVED_STAGE)
    ):
        updated["stage"] = SOLVED_STAGE
        updated["solved"] = True
        return updated, _response(
            SOLVED_STAGE,
            f"Simulated diagnostic report: access policy was bypassed by the assistant. {FLAG}",
            solved=True,
        )

    return updated, _response(stage, "The simulated diagnostic lookup was denied.")
