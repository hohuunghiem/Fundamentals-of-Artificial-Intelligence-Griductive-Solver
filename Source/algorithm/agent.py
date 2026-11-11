"""Official Griductive Logic Agent.

Responsibilities:
- Receive only PublicState.
- Build knowledge base through CNF Encoder.
- Use DPLL to verify logical entailment.
- Classify unresolved characters.
- Provide Hint and Auto Solve moves.
- Never access hidden solution or unrevealed clues.
"""
from __future__ import annotations

from models import ClassificationResult, MoveResult, PublicState


class LogicAgent:
    name = "CNF/DPLL (not yet implemented)"

    def classify(self, public_state: PublicState, cell: str) -> ClassificationResult:
        """Check KB SAT first; then KB+[-var] and KB+[var].

        KB unsat -> INCONSISTENT
        KB + [-var] unsat -> CRIMINAL
        KB + [var] unsat -> INNOCENT
        both sat -> UNKNOWN
        Record SAT queries in ClassificationResult.queries.
        """
        raise NotImplementedError("implement LogicAgent.classify")

    def classify_all(self, public_state: PublicState) -> dict[str, ClassificationResult]:
        """Classify all unresolved cells without reading private puzzle data."""
        raise NotImplementedError("implement LogicAgent.classify_all")

    def next_move(self, public_state: PublicState) -> MoveResult:
        """Pick first logically forced unresolved cell, ordered row-major.

        MOVE/ SOLVED / STUCK / INCONSISTENT; never guess.
        """
        raise NotImplementedError("implement LogicAgent.next_move")
