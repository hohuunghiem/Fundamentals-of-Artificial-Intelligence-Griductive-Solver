"""GameEngine: authoritative private game state and strictly public snapshots.

No caller receives the full PuzzleData. In particular, GUI and LogicAgent
must only receive get_public_state() and SubmitResult.public_state.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from models import PublicState, SubmitResult
from regions import all_cells
from semantics import evaluate_clue, validate_clue


class GameEngine:
    def __init__(self, agent: Any):
        if agent is None:
            raise ValueError(
                "GameEngine requires a LogicAgent instance"
            )

        self._agent = agent
        self._puzzle: dict[str, Any] | None = None
        self._revealed: set[str] = set()

    @property
    def agent(self) -> Any:
        """Only exposes the logic agent, NEVER secret puzzle data."""
        return self._agent

    @staticmethod
    def _validated_data(data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError("Puzzle root must be a JSON object")
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            raise ValueError("Unsupported schema_version (expected 1)")
        size = data.get("size")
        cells = all_cells(size)
        if not isinstance(data.get("puzzle_id"), str) or not data["puzzle_id"].strip():
            raise ValueError("puzzle_id must be non-empty")
        people = data.get("characters")
        if not isinstance(people, list) or len(people) != len(cells):
            raise ValueError(f"characters must have exactly {len(cells)} entries")
        by_cell = {}
        for character in people:
            if not isinstance(character, dict):
                raise ValueError("Each character must be an object")
            cell = character.get("cell")
            if cell in by_cell or cell not in cells:
                raise ValueError(f"Duplicate or invalid character cell: {cell!r}")
            if not all(isinstance(character.get(field), str) and character[field].strip()
                       for field in ("name", "profession")):
                raise ValueError(f"Character {cell}: name/profession required")
            by_cell[cell] = {k: character[k] for k in ("cell", "name", "profession")}
        if set(by_cell) != set(cells):
            raise ValueError("Characters must cover all board cells")
        names = [by_cell[c]["name"].casefold() for c in cells]
        if names != sorted(names) or len(names) != len(set(names)):
            raise ValueError("Character names must be unique and alphabetically sorted row-major")
        solution = data.get("solution")
        if not isinstance(solution, dict) or set(solution) != set(cells):
            raise ValueError("solution must assign exactly all cells")
        if any(type(status) is not bool for status in solution.values()):
            raise ValueError("solution values must be boolean")
        clues = data.get("clues")
        if not isinstance(clues, list) or len(clues) != len(cells):
            raise ValueError("Each character must own exactly one clue")
        owned = {}
        ids = set()
        for clue in clues:
            validate_clue(clue, size)
            if clue["owner"] in owned or clue["id"] in ids:
                raise ValueError("Clue owner and id must each be unique")
            ids.add(clue["id"])
            owned[clue["owner"]] = deepcopy(clue)
            if not evaluate_clue(clue, solution, size):
                raise ValueError(f"Clue {clue['id']} contradicts hidden solution")
        if set(owned) != set(cells):
            raise ValueError("Every card must have one clue")
        initial = data.get("initial_revealed")
        if not isinstance(initial, list) or not initial or len(initial) != len(set(initial)):
            raise ValueError("initial_revealed must be a nonempty unique list")
        if any(c not in cells for c in initial):
            raise ValueError("initial_revealed contains unknown cell")
        # Commit only normalized, validated data, not arbitrary additional input fields.
        return {
            "puzzle_id": data["puzzle_id"], "size": size,
            "characters": [by_cell[c] for c in cells],
            "solution": dict(solution), "clues_by_owner": owned,
            "initial_revealed": list(initial),
        }

    def load_puzzle(self, path: str | Path) -> PublicState:
        try:
            with Path(path).open(encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot read puzzle: {e}") from e
        return self.load_data(raw)

    def load_data(self, data: dict) -> PublicState:
        """Useful for testing; validation happens before existing state is replaced."""
        candidate = self._validated_data(deepcopy(data))
        self._puzzle = candidate
        self._revealed = set(candidate["initial_revealed"])
        return self.get_public_state()

    def restart(self) -> PublicState:
        puzzle = self._require_puzzle()
        self._revealed = set(puzzle["initial_revealed"])
        return self.get_public_state()

    def _require_puzzle(self) -> dict:
        if self._puzzle is None:
            raise RuntimeError("Load a puzzle first")
        return self._puzzle

    def get_public_state(self) -> PublicState:
        puzzle = self._require_puzzle()
        cells = all_cells(puzzle["size"])
        revealed = [c for c in cells if c in self._revealed]
        public = {
            "puzzle_id": puzzle["puzzle_id"],
            "size": puzzle["size"],
            "characters": puzzle["characters"],
            "known_statuses": {c: puzzle["solution"][c] for c in revealed},
            "revealed_clues": [puzzle["clues_by_owner"][c] for c in revealed],
        }
        return deepcopy(public)

    def submit_verdict(self, cell: str, verdict: str) -> SubmitResult:
        puzzle = self._require_puzzle()
        old_state = self.get_public_state()
        if cell not in all_cells(puzzle["size"]):
            return SubmitResult("INVALID_CELL", old_state, message="Unknown cell")
        if verdict not in ("CRIMINAL", "INNOCENT"):
            return SubmitResult("INVALID_VERDICT", old_state, message="Choose CRIMINAL or INNOCENT")
        if cell in self._revealed:
            return SubmitResult("ALREADY_REVEALED", old_state, message="Card already face-up")
        # Critical trust boundary: ONLY public_state, never puzzle/solution/hidden clues.
        conclusion = self._agent.classify(deepcopy(old_state), cell)
        if conclusion.status == "INCONSISTENT":
            return SubmitResult("INCONSISTENT", old_state, message="Public knowledge is inconsistent")
        if conclusion.status == "UNKNOWN":
            return SubmitResult("NOT_PROVABLE", old_state, message="Cannot prove either verdict")
        if conclusion.status not in ("CRIMINAL", "INNOCENT"):
            raise ValueError(f"Agent returned invalid classification: {conclusion.status}")
        if conclusion.status != verdict:
            return SubmitResult("CONTRADICTED", old_state, message=f"The forced verdict is {conclusion.status}")
        expected = "CRIMINAL" if puzzle["solution"][cell] else "INNOCENT"
        if verdict != expected:
            return SubmitResult("PUZZLE_ERROR", old_state, message="Proof contradicts hidden puzzle solution")
        self._revealed.add(cell)
        new_state = self.get_public_state()
        visible_clue = next(c for c in new_state["revealed_clues"] if c["owner"] == cell)
        return SubmitResult("ACCEPTED", new_state, deepcopy(visible_clue), "Card revealed",
                            tuple(deepcopy(q) for q in conclusion.queries))
