"""So CNF với semantic evaluator trên MỌI phép gán (brute force)."""
import sys, os
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from itertools import product
from algorithm.encoder import encode_clue, build_var_map, encode
from regions import all_cells, resolve_region
from semantics import evaluate_clue

SIZE = 3
CELLS = all_cells(SIZE)
VAR = build_var_map(SIZE)
VAR_INV = {v: c for c, v in VAR.items()}


def cnf_true(clauses, assign):
    return all(any(assign[VAR_INV[abs(l)]] == (l > 0) for l in cl) for cl in clauses)


clues = [
    {"id": "f1", "type": "FACT", "cell": "B2", "criminal": True},
    {"id": "f2", "type": "FACT", "cell": "A1", "criminal": False},
    {"id": "s", "type": "SAME", "cells": ["A1", "C3"]},
    {"id": "d", "type": "DIFFERENT", "cells": ["B1", "B2"]},
]
regions = [
    {"kind": "ROW", "index": 2}, {"kind": "COLUMN", "label": "C"},
    {"kind": "NEIGHBORS", "cell": "B2"}, {"kind": "NEIGHBORS", "cell": "A1"},
    {"kind": "CELLS", "cells": ["A1", "C3"]}, {"kind": "CORNERS"},
    {"kind": "COMMON_NEIGHBORS", "cells": ["A1", "C1"]},
]
for t in ("EXACTLY", "AT_LEAST", "AT_MOST"):
    for r in regions:
        for k in range(len(resolve_region(r, SIZE)) + 1):
            clues.append({"id": f"{t}{k}", "type": t, "k": k, "region": r})


bad = [
    {"id": "b1", "type": "EXACTLY", "k": 4, "region": {"kind": "ROW", "index": 1}},
    {"id": "b2", "type": "EXACTLY", "k": True, "region": {"kind": "ROW", "index": 1}},
    {"id": "b3", "type": "SAME", "cells": ["A1", "A1"]},
    {"id": "b4", "type": "FACT", "cell": "D1", "criminal": True},
]
class EncoderTests(unittest.TestCase):
    def test_cnf_matches_semantics_exhaustively(self):
        for clue in clues:
            cnf = encode_clue(clue, SIZE, VAR)
            for bits in product([False, True], repeat=len(CELLS)):
                a = dict(zip(CELLS, bits))
                self.assertEqual(cnf_true(cnf, a), evaluate_clue(clue, a, SIZE), (clue, a))

    def test_invalid_clues(self):
        for clue in bad + [None, {}, {"type": "FACT", "cell": "A01", "criminal": True}]:
            with self.subTest(clue=clue), self.assertRaises(ValueError):
                encode_clue(clue, SIZE, VAR)

    def test_empty_regions_and_boundaries(self):
        for kind in ("EXACTLY", "AT_LEAST", "AT_MOST"):
            clue = {"type": kind, "k": 0, "region": {"kind": "CELLS", "cells": []}}
            self.assertEqual(encode_clue(clue, 3, VAR), [])
        for kind, expected in (("AT_MOST", [[-1], [-2], [-3]]),
                               ("AT_LEAST", [[1], [2], [3]])):
            clue = {"type": kind, "k": 0 if kind == "AT_MOST" else 3,
                    "region": {"kind": "ROW", "index": 1}}
            self.assertEqual(encode_clue(clue, 3, VAR), expected)

    def test_public_only_counts_no_mutation(self):
        state = {"size": 3, "revealed_clues": [clues[0]], "known_statuses": {"A1": False},
                 "solution": {"A1": True}, "clues": [{"invalid": "hidden"}]}
        before = deepcopy(state)
        kb = encode(state)
        self.assertEqual(kb.clauses, [[5], [-1]])
        self.assertEqual((kb.primary_count, kb.aux_count, kb.num_vars, kb.clause_count), (9, 0, 9, 2))
        self.assertEqual(state, before)
        for size in (3, 4, 5):
            kb = encode({"size": size, "revealed_clues": [], "known_statuses": {}})
            self.assertEqual(list(kb.cell_to_var), all_cells(size))
            self.assertEqual(list(kb.cell_to_var.values()), list(range(1, size * size + 1)))
            self.assertEqual(kb.clauses, [])
            self.assertEqual(kb.num_vars, size * size)

    def test_invalid_public_state(self):
        for state in (None, {}, {"size": 2},
                      {"size": 3, "revealed_clues": [], "known_statuses": {"A1": "False"}},
                      {"size": 3, "revealed_clues": None, "known_statuses": {}},
                      {"size": 3, "revealed_clues": [], "known_statuses": []}):
            with self.subTest(state=state), self.assertRaises(ValueError):
                encode(state)

    def test_conflicting_public_information_is_preserved(self):
        kb = encode({"size": 3, "known_statuses": {"A1": False},
                     "revealed_clues": [{"type": "FACT", "cell": "A1", "criminal": True}]})
        self.assertEqual(kb.clauses, [[1], [-1]])

    def test_all_bundled_puzzles_semantics_and_counts(self):
        for path in (Path(__file__).resolve().parents[1] / "puzzles").glob("*.json"):
            puzzle = json.loads(path.read_text(encoding="utf-8"))
            kb = encode({"size": puzzle["size"], "revealed_clues": puzzle["clues"],
                         "known_statuses": {}})
            self.assertEqual(kb.clause_count, len(kb.clauses))
            self.assertEqual(kb.primary_count, puzzle["size"] ** 2)
            self.assertTrue(all(any(puzzle["solution"][cell] == (literal > 0)
                                   for literal in clause
                                   for cell, v in kb.cell_to_var.items() if v == abs(literal))
                                for clause in kb.clauses), path.name)

    def test_agent_uses_real_encoder(self):
        from algorithm.agent import LogicAgent
        from models import SATResult
        with patch("algorithm.agent.solve", side_effect=[SATResult("SAT", {}),
                   SATResult("UNSAT", None), SATResult("SAT", {})]) as solver:
            result = LogicAgent().classify({"size": 3, "known_statuses": {},
                "revealed_clues": [{"type": "FACT", "cell": "A1", "criminal": True, "id": "fact"}]}, "A1")
        self.assertEqual(result.status, "CRIMINAL")
        self.assertEqual(solver.call_args_list[1].args, ([[1], [-1]], 9))


if __name__ == "__main__":
    unittest.main()
