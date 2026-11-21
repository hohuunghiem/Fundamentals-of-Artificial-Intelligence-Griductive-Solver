"""DPLL SAT solver.

This module intentionally has no knowledge of boards, cells, or the GUI.
"""
from __future__ import annotations

from time import perf_counter

from models import SATResult, SATStats


def _literal_value(literal: int, assignment: dict[int, bool]) -> bool | None:
    variable = abs(literal)
    if variable not in assignment:
        return None
    value = assignment[variable]
    return value if literal > 0 else not value


def _propagate(
    clauses: list[list[int]],
    assignment: dict[int, bool],
    stats: dict[str, int],
) -> bool:
    """Apply unit clauses repeatedly. Return False on an immediate conflict."""
    changed = True
    while changed:
        changed = False

        for clause in clauses:
            satisfied = False
            unassigned: list[int] = []

            for literal in clause:
                value = _literal_value(literal, assignment)
                if value is True:
                    satisfied = True
                    break
                if value is None:
                    unassigned.append(literal)

            if satisfied:
                continue
            if not unassigned:
                return False
            if len(unassigned) == 1:
                literal = unassigned[0]
                variable = abs(literal)
                value = literal > 0

                if variable in assignment and assignment[variable] != value:
                    return False
                if variable not in assignment:
                    assignment[variable] = value
                    stats["propagations"] += 1
                    changed = True

    return True


def _search(
    clauses: list[list[int]],
    num_vars: int,
    assignment: dict[int, bool],
    stats: dict[str, int],
) -> bool:
    if not _propagate(clauses, assignment, stats):
        return False

    unresolved = [
        variable
        for variable in range(1, num_vars + 1)
        if variable not in assignment
    ]

    if not unresolved:
        return all(
            any(_literal_value(literal, assignment) is True for literal in clause)
            for clause in clauses
        )

    variable = unresolved[0]
    stats["decisions"] += 1

    for value in (True, False):
        branch = assignment.copy()
        branch[variable] = value
        if _search(clauses, num_vars, branch, stats):
            assignment.clear()
            assignment.update(branch)
            return True
        stats["backtracks"] += 1

    return False


def solve(clauses: list[list[int]], num_vars: int) -> SATResult:
    """Solve a CNF formula and return SAT/UNSAT with complete-model statistics."""
    started = perf_counter()

    if type(num_vars) is not int or num_vars < 0:
        raise ValueError("num_vars must be a non-negative integer")
    if not isinstance(clauses, list):
        raise ValueError("clauses must be a list")

    formula: list[list[int]] = []
    for clause in clauses:
        if not isinstance(clause, list):
            raise ValueError("Each clause must be a list")
        copied: list[int] = []
        for literal in clause:
            if type(literal) is not int:
                raise ValueError("Literals must be integers")
            if literal == 0 or abs(literal) > num_vars:
                raise ValueError(
                    f"Literal {literal} is outside the variable range 1..{num_vars}"
                )
            copied.append(literal)
        formula.append(copied)

    stats = {"decisions": 0, "propagations": 0, "backtracks": 0}
    assignment: dict[int, bool] = {}
    satisfiable = _search(formula, num_vars, assignment, stats)
    runtime_ms = (perf_counter() - started) * 1000
    sat_stats = SATStats(
        decisions=stats["decisions"],
        propagations=stats["propagations"],
        backtracks=stats["backtracks"],
        runtime_ms=runtime_ms,
    )

    if not satisfiable:
        return SATResult("UNSAT", None, sat_stats)

    complete_assignment = {
        variable: assignment.get(variable, False)
        for variable in range(1, num_vars + 1)
    }
    return SATResult("SAT", complete_assignment, sat_stats)
