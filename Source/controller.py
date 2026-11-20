"""Public-only orchestration. Never caches the hidden puzzle or complete solution."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from engine import GameEngine
from models import MoveResult, PublicState, SubmitResult


class GameController:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.trace: list[dict[str, Any]] = []
        self.step = 0

    def load(self, path: str | Path) -> PublicState:
        state = self.engine.load_puzzle(path)
        self.trace.clear()
        self.step = 0
        return state

    def restart(self) -> PublicState:
        state = self.engine.restart()
        self.trace.clear()
        self.step = 0
        return state

    def hint(self) -> MoveResult:
        return self.engine.agent.next_move(self.engine.get_public_state())

    def submit(self, cell: str, verdict: str) -> SubmitResult:
        before = self.engine.get_public_state()
        result = self.engine.submit_verdict(cell, verdict)
        if result.status == "ACCEPTED":
            self.step += 1
            self.trace.append({
                "step": self.step,
                "active_clue_ids": [c["id"] for c in before["revealed_clues"]],
                "sat_queries": [deepcopy(query) for query in result.sat_queries],
                "cell": cell,
                "verdict": verdict,
                "newly_revealed_clue": deepcopy(result.revealed_clue),
            })
        return result

    def auto_step(self) -> tuple[MoveResult, SubmitResult | None]:
        move = self.hint()
        if move.status != "MOVE":
            return move, None
        result = self.submit(move.cell, move.verdict)
        if result.status == "ACCEPTED" and self.trace:
            self.trace[-1]["sat_queries"] = (
                [deepcopy(query) for query in move.queries]
                + self.trace[-1]["sat_queries"]
            )
        return move, result
