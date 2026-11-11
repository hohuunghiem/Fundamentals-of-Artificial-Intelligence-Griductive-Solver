"""TODO -- teammate 4: offline uniqueness and no-guess playthrough checks.

Offline validation is permitted to read full puzzle data; gameplay agent is NOT.
"""
from __future__ import annotations


def check_uniqueness(puzzle: dict) -> str:
    """Return UNIQUE / MULTIPLE / INCONSISTENT using TWO SAT calls.

    Encode ALL clues (not the solution labels as unit clauses). If SAT, create
    one blocking clause for PRIMARY variables only and solve again. Check the
    unique assignment matches the hidden solution independently.
    """
    raise NotImplementedError("Teammate 4: implement offline uniqueness check")


def check_progressive_solvability(puzzle: dict) -> dict:
    """Run with public reveals only, detect STUCK even for unique puzzles."""
    raise NotImplementedError("Teammate 4: implement progressive solve check")
