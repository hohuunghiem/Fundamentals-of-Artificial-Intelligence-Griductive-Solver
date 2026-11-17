"""Entailment agent using only public knowledge."""
from dataclasses import asdict
from algorithm.encoder import encode
from algorithm.dpll import solve
from models import ClassificationResult, MoveResult


def _query(kb, assumptions=()):
    result = solve(kb.clauses + [[v] for v in assumptions], kb.num_vars)
    return {"assumptions": list(assumptions), "status": result.status,
            "stats": asdict(result.stats)}


def _classify(kb, cell, base, clues):
    if base["status"] == "UNSAT":
        return ClassificationResult("INCONSISTENT", (base,))
    v = kb.cell_to_var[cell]
    negative, positive = _query(kb, (-v,)), _query(kb, (v,))
    status = ("CRIMINAL" if negative["status"] == "UNSAT" else
              "INNOCENT" if positive["status"] == "UNSAT" else "UNKNOWN")
    # All active premises; these IDs do not claim a minimal proof core.
    return ClassificationResult(status, (base, negative, positive), clues)


class LogicAgent:
    name = "CNF/DPLL"

    def classify(self, public_state, cell):
        kb = encode(public_state)
        if cell not in kb.cell_to_var:
            raise ValueError(f"Unknown cell: {cell!r}")
        return _classify(kb, cell, _query(kb),
                         tuple(c["id"] for c in public_state["revealed_clues"]))

    def classify_all(self, public_state):
        kb = encode(public_state)
        base = _query(kb)
        clues = tuple(c["id"] for c in public_state["revealed_clues"])
        return {cell: _classify(kb, cell, base, clues) for cell in kb.cell_to_var
                if cell not in public_state["known_statuses"]}

    def next_move(self, public_state):
        kb = encode(public_state)
        base = _query(kb)
        if base["status"] == "UNSAT":
            return MoveResult("INCONSISTENT", queries=(base,))
        clues = tuple(c["id"] for c in public_state["revealed_clues"])
        queries = [base]
        unresolved = [c for c in kb.cell_to_var if c not in public_state["known_statuses"]]
        for cell in unresolved:
            result = _classify(kb, cell, base, clues)
            queries.extend(result.queries[1:])
            if result.status in ("CRIMINAL", "INNOCENT"):
                return MoveResult("MOVE", cell, result.status, tuple(queries), clues)
        return MoveResult("STUCK" if unresolved else "SOLVED", queries=tuple(queries))
