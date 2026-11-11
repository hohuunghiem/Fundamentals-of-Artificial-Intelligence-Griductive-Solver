"""Direct semantic evaluator; deliberately independent of CNF or SAT.

Baseline is supplied for puzzle-data safety. Encoder owner should extend tests
and verify CNF equivalence against this independent evaluator.
"""
from __future__ import annotations

from regions import all_cells, resolve_region


def validate_clue(clue: dict, size: int) -> None:
    if not isinstance(clue, dict) or not isinstance(clue.get("id"), str) or not clue["id"]:
        raise ValueError("Clue must have a non-empty id")
    if clue.get("owner") not in all_cells(size):
        raise ValueError(f"Invalid clue owner: {clue.get('owner')!r}")
    kind = clue.get("type")
    if kind == "FACT":
        if clue.get("cell") not in all_cells(size) or type(clue.get("criminal")) is not bool:
            raise ValueError(f"Invalid FACT clue: {clue['id']}")
    elif kind in ("SAME", "DIFFERENT"):
        cells = clue.get("cells")
        if (not isinstance(cells, list) or len(cells) != 2
                or len(set(map(str, cells))) != 2 or any(c not in all_cells(size) for c in cells)):
            raise ValueError(f"Invalid {kind} clue: {clue['id']}")
    elif kind in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        cells = resolve_region(clue.get("region"), size)
        k = clue.get("k")
        if type(k) is not int or not (0 <= k <= len(cells)):
            raise ValueError(f"Invalid counting k for {clue['id']}")
    else:
        raise ValueError(f"Unsupported clue type: {kind!r}")


def evaluate_clue(clue: dict, assignment: dict[str, bool], board: int) -> bool:
    """Return truth value under a COMPLETE assignment. No calls to encoder."""
    validate_clue(clue, board)
    required = set(all_cells(board))
    if not isinstance(assignment, dict) or set(assignment) != required:
        raise ValueError("Assignment must cover every cell exactly once")
    if any(type(v) is not bool for v in assignment.values()):
        raise ValueError("Assignment values must be boolean")
    kind = clue["type"]
    if kind == "FACT":
        return assignment[clue["cell"]] == clue["criminal"]
    if kind == "SAME":
        a, b = clue["cells"]
        return assignment[a] == assignment[b]
    if kind == "DIFFERENT":
        a, b = clue["cells"]
        return assignment[a] != assignment[b]
    count = sum(assignment[c] for c in resolve_region(clue["region"], board))
    if kind == "EXACTLY":
        return count == clue["k"]
    if kind == "AT_LEAST":
        return count >= clue["k"]
    return count <= clue["k"]
