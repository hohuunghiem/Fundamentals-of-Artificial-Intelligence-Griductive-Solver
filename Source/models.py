"""Stable, shared contracts for the Game Engine, encoder, DPLL and Logic Agent.

Do not rename these fields without coordinating with all team members.
PublicState is a plain JSON-compatible dictionary (deep-copied at API boundaries).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

PublicState = dict[str, Any]
Verdict = Literal["CRIMINAL", "INNOCENT"]


@dataclass(frozen=True)
class SATStats:
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime_ms: float = 0.0


@dataclass(frozen=True)
class SATResult:
    status: Literal["SAT", "UNSAT"]
    assignment: dict[int, bool] | None
    stats: SATStats = field(default_factory=SATStats)


@dataclass(frozen=True)
class EncodedKB:
    clauses: list[list[int]]
    cell_to_var: dict[str, int]
    primary_count: int
    aux_count: int
    num_vars: int
    clause_count: int


@dataclass(frozen=True)
class ClassificationResult:
    status: Literal["CRIMINAL", "INNOCENT", "UNKNOWN", "INCONSISTENT"]
    queries: tuple[dict[str, Any], ...] = ()
    relevant_clue_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MoveResult:
    status: Literal["MOVE", "SOLVED", "STUCK", "INCONSISTENT"]
    cell: str | None = None
    verdict: Verdict | None = None
    queries: tuple[dict[str, Any], ...] = ()
    relevant_clue_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SubmitResult:
    status: str
    public_state: PublicState
    revealed_clue: dict[str, Any] | None = None
    message: str = ""
    sat_queries: tuple[dict[str, Any], ...] = ()
