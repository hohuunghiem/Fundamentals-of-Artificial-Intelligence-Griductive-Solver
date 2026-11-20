"""Requirement 4.4 contract tests; encoder and solver are owned by 4.2/4.3."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from algorithm.agent import LogicAgent
from models import EncodedKB, SATResult


def kb():
    return EncodedKB([], {"A1": 1, "B1": 2}, 2, 0, 2, 0)


def sat():
    return SATResult("SAT", {1: False, 2: False})


def unsat():
    return SATResult("UNSAT", None)


class AgentContractTests(unittest.TestCase):
    def setUp(self):
        self.state = {"size": 3, "known_statuses": {}, "revealed_clues": []}
        self.encoder = patch("algorithm.agent.encode", return_value=kb()).start()
        self.solver = patch("algorithm.agent.solve").start()
        self.addCleanup(patch.stopall)

    def test_classifications_and_assumptions(self):
        for results, expected in (([sat(), unsat(), sat()], "CRIMINAL"),
                                  ([sat(), sat(), unsat()], "INNOCENT"),
                                  ([sat(), sat(), sat()], "UNKNOWN")):
            with self.subTest(expected=expected):
                self.solver.reset_mock()
                self.solver.side_effect = results
                result = LogicAgent().classify(self.state, "A1")
                self.assertEqual(result.status, expected)
                self.assertEqual([q["assumptions"] for q in result.queries], [[], [-1], [1]])
                self.assertEqual([c.args[0] for c in self.solver.call_args_list], [[], [[-1]], [[1]]])
                self.assertEqual(kb().clauses, [])

    def test_inconsistent_precedes_solved(self):
        self.state["known_statuses"] = {"A1": False, "B1": False}
        self.solver.return_value = unsat()
        self.assertEqual(LogicAgent().next_move(self.state).status, "INCONSISTENT")
        self.assertEqual(self.solver.call_count, 1)

    def test_classify_all_excludes_known(self):
        self.state["known_statuses"] = {"A1": False}
        self.solver.side_effect = [sat(), sat(), sat()]
        results = LogicAgent().classify_all(self.state)
        self.assertEqual(list(results), ["B1"])
        self.assertEqual(results["B1"].status, "UNKNOWN")

    def test_next_move_keeps_queries_for_skipped_unknown(self):
        self.solver.side_effect = [sat(), sat(), sat(), unsat(), sat()]
        move = LogicAgent().next_move(self.state)
        self.assertEqual((move.status, move.cell, move.verdict), ("MOVE", "B1", "CRIMINAL"))
        self.assertEqual(len(move.queries), 5)

    def test_terminal_states_and_no_mutation(self):
        before = deepcopy(self.state)
        self.solver.return_value = sat()
        self.assertEqual(LogicAgent().next_move(self.state).status, "STUCK")
        self.assertEqual(before, self.state)
        self.state["known_statuses"] = {"A1": False, "B1": False}
        self.assertEqual(LogicAgent().next_move(self.state).status, "SOLVED")
        with self.assertRaises(ValueError):
            LogicAgent().classify(self.state, "Z9")

