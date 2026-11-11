"""TODO -- teammate 3: implement DPLL with stats and complete models.

No third-party SAT backend. This solver should NOT know about board/cells/UI.
"""
from __future__ import annotations

from models import SATResult


def solve(clauses: list[list[int]], num_vars: int) -> SATResult:
    """Return SAT/UNSAT and per-query statistics.

    Must implement: unit propagation, conflict check, deterministic variable
    selection (lowest unassigned ID), branching True then False, recursion,
    backtracking, full satisfying assignment 1..num_vars, runtime_ms.
    Do not mutate input clauses. Do not mistake an arbitrary model for proof.
    """
    raise NotImplementedError("Teammate 3: implement DPLL solve(clauses, num_vars)")
