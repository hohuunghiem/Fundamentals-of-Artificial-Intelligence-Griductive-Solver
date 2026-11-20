"""Baseline integration tests for Engine / geometry / no-guess guardrails.

Run from Source/: python -m unittest discover -s tests -v
Encoder / DPLL tests should be added by their owners to tests/test_encoder.py etc.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from algorithm.agent import LogicAgent
from controller import GameController
from engine import GameEngine
from models import ClassificationResult
from regions import all_cells, referenced_cells, resolve_region
from semantics import evaluate_clue

ROOT = Path(__file__).resolve().parents[1]
DEMO3 = ROOT / "puzzles" / "demo_3x3.json"
DEMO4 = ROOT / "puzzles" / "demo_4x4.json"


class RegionTests(unittest.TestCase):
    def test_row_major(self):
        self.assertEqual(all_cells(3), ["A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3"])

    def test_row_and_column(self):
        self.assertEqual(resolve_region({"kind": "ROW", "index": 2}, 3), ["A2", "B2", "C2"])
        self.assertEqual(resolve_region({"kind": "COLUMN", "label": "C"}, 3), ["C1", "C2", "C3"])

    def test_neighbors_include_diagonals_not_self(self):
        self.assertEqual(resolve_region({"kind": "NEIGHBORS", "cell": "B2"}, 3),
                         ["A1", "B1", "C1", "A2", "C2", "A3", "B3", "C3"])
        self.assertEqual(resolve_region({"kind": "NEIGHBORS", "cell": "A1"}, 3),
                         ["B1", "A2", "B2"])

    def test_explicit_sort_and_duplicate_rejection(self):
        self.assertEqual(resolve_region({"kind": "CELLS", "cells": ["C3", "B1", "A2"]}, 3),
                         ["B1", "A2", "C3"])
        with self.assertRaises(ValueError):
            resolve_region({"kind": "CELLS", "cells": ["A1", "A1"]}, 3)

    def test_extensions(self):
        self.assertEqual(resolve_region({"kind": "CORNERS"}, 3), ["A1", "C1", "A3", "C3"])
        self.assertEqual(resolve_region({"kind": "COMMON_NEIGHBORS", "cells": ["A1", "C1"]}, 3), ["B1", "B2"])

    def test_empty_intersection(self):
        self.assertEqual(resolve_region({"kind": "COMMON_NEIGHBORS", "cells": ["A1", "C3"]}, 3), ["B2"])

    def test_bad_regions(self):
        for region in ({"kind": "ROW", "index": True}, {"kind": "ROW", "index": 4},
                       {"kind": "COLUMN", "label": "Z"},
                       {"kind": "COMMON_NEIGHBORS", "cells": ["A1", "A1"]},
                       {"kind": "UNKNOWN"}):
            with self.subTest(region=region), self.assertRaises(ValueError):
                resolve_region(region, 3)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(LogicAgent())
        self.state = self.engine.load_puzzle(DEMO3)

    def test_only_initial_card_revealed(self):
        self.assertEqual(set(self.state["known_statuses"]), {"A1"})
        self.assertEqual([c["owner"] for c in self.state["revealed_clues"]], ["A1"])
        self.assertEqual(len(self.state["characters"]), 9)

    def test_public_does_not_leak_solution_hidden_clue_or_file(self):
        self.assertNotIn("solution", self.state)
        self.assertNotIn("clues", self.state)
        self.assertNotIn("clues_by_owner", self.state)
        self.assertNotIn("initial_revealed", self.state)
        self.assertNotIn("path", self.state)
        self.assertNotIn("clue_C3", str(self.state))
        self.assertNotIn("criminal", str(self.state["characters"]))

    def test_snapshot_is_defensive_deep_copy(self):
        self.state["known_statuses"]["A1"] = True
        self.state["revealed_clues"][0]["criminal"] = False
        self.state["characters"][0]["name"] = "MODIFIED"
        other = self.engine.get_public_state()
        self.assertFalse(other["known_statuses"]["A1"])
        self.assertTrue(other["revealed_clues"][0]["criminal"])
        self.assertEqual(other["characters"][0]["name"], "An")

    def test_not_provable_does_not_flip(self):
        before = deepcopy(self.engine.get_public_state())
        self.assertEqual(self.engine.submit_verdict("C3", "INNOCENT").status, "NOT_PROVABLE")
        self.assertEqual(before, self.engine.get_public_state())

    def test_contradicted_does_not_flip(self):
        before = deepcopy(self.engine.get_public_state())
        result = self.engine.submit_verdict("B1", "INNOCENT")
        self.assertEqual(result.status, "CONTRADICTED")
        self.assertEqual(result.revealed_clue, None)
        self.assertEqual(before, self.engine.get_public_state())

    def test_accept_flips_only_target(self):
        result = self.engine.submit_verdict("B1", "CRIMINAL")
        self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(set(result.public_state["known_statuses"]), {"A1", "B1"})
        self.assertEqual(result.revealed_clue["owner"], "B1")
        self.assertEqual(len(result.public_state["revealed_clues"]), 2)

    def test_reject_bad_or_repeat(self):
        for cell, verdict, expected in (("ZZ", "CRIMINAL", "INVALID_CELL"),
                                        ("B1", "RANDOM", "INVALID_VERDICT"),
                                        ("A1", "INNOCENT", "ALREADY_REVEALED")):
            self.assertEqual(self.engine.submit_verdict(cell, verdict).status, expected)

    def test_restart_removes_reveals(self):
        self.engine.submit_verdict("B1", "CRIMINAL")
        state = self.engine.restart()
        self.assertEqual(list(state["known_statuses"]), ["A1"])

    def test_invalid_load_is_atomic(self):
        data = deepcopy(self._read_demo())
        data["solution"]["B1"] = False  # makes clue_A1 false
        with self.assertRaisesRegex(ValueError, "contradicts"):
            self.engine.load_data(data)
        self.assertEqual(set(self.engine.get_public_state()["known_statuses"]), {"A1"})

    def test_reject_bad_count_k_bool(self):
        data = deepcopy(self._read_demo())
        data["clues"][-1]["k"] = True
        with self.assertRaises(ValueError):
            self.engine.load_data(data)

    def test_agent_receives_public_only(self):
        class SpyAgent:
            seen = None
            def classify(self, public_state, cell):
                self.seen = deepcopy(public_state)
                public_state["revealed_clues"].clear()  # should not corrupt Engine
                return ClassificationResult("UNKNOWN")
        spy = SpyAgent()
        engine = GameEngine(spy)
        engine.load_puzzle(DEMO3)
        result = engine.submit_verdict("B1", "CRIMINAL")
        self.assertEqual(result.status, "NOT_PROVABLE")
        self.assertNotIn("solution", spy.seen)
        self.assertEqual(len(engine.get_public_state()["revealed_clues"]), 1)

    def test_faulty_agent_must_not_flip_against_answer(self):
        class FaultyAgent:
            def classify(self, state, cell):
                return ClassificationResult("CRIMINAL")
        engine = GameEngine(FaultyAgent())
        engine.load_puzzle(DEMO3)
        self.assertEqual(engine.submit_verdict("A2", "CRIMINAL").status, "PUZZLE_ERROR")
        self.assertEqual(set(engine.get_public_state()["known_statuses"]), {"A1"})

    @staticmethod
    def _read_demo():
        import json
        return json.loads(DEMO3.read_text(encoding="utf-8"))


class LogicAndIntegrationTests(unittest.TestCase):
    def test_evaluate_six_templates(self):
        e = GameEngine(LogicAgent())
        e.load_puzzle(DEMO3)
        data = EngineTests._read_demo()
        answer = data["solution"]
        for clue in data["clues"]:
            self.assertTrue(evaluate_clue(clue, answer, 3))
        same = {"id": "same", "owner": "A1", "type": "SAME", "cells": ["A1", "A2"]}
        different = {"id": "diff", "owner": "A1", "type": "DIFFERENT", "cells": ["A1", "B1"]}
        least = {"id": "least", "owner": "A1", "type": "AT_LEAST", "k": 1,
                 "region": {"kind": "ROW", "index": 1}}
        most = {"id": "most", "owner": "A1", "type": "AT_MOST", "k": 2,
                "region": {"kind": "ROW", "index": 1}}
        for clue in (same, different, least, most):
            self.assertTrue(evaluate_clue(clue, answer, 3))

    def test_referenced_cells(self):
        clue = {"type": "AT_LEAST", "k": 1, "region": {"kind": "COLUMN", "label": "B"}}
        self.assertEqual(referenced_cells(clue, 3), ["B1", "B2", "B3"])

    def test_auto_solve_demo_3x3_and_trace(self):
        controller = GameController(GameEngine(LogicAgent()))
        controller.load(DEMO3)
        for _ in range(9):
            move, result = controller.auto_step()
            if result is None:
                self.assertEqual(move.status, "SOLVED")
                break
            self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(len(controller.trace), 8)
        self.assertEqual(len(controller.engine.get_public_state()["known_statuses"]), 9)
        for step, entry in enumerate(controller.trace, start=1):
            self.assertEqual(entry["step"], step)
            self.assertIn("active_clue_ids", entry)
            self.assertIn("sat_queries", entry)
            self.assertEqual(entry["newly_revealed_clue"]["owner"], entry["cell"])

    def test_auto_solve_demo_4x4(self):
        controller = GameController(GameEngine(LogicAgent()))
        controller.load(DEMO4)
        for _ in range(16):
            move, result = controller.auto_step()
            if result is None:
                self.assertEqual(move.status, "SOLVED")
                break
            self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(len(controller.engine.get_public_state()["known_statuses"]), 16)


if __name__ == "__main__":
    unittest.main()
