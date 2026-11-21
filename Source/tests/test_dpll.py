import unittest

from algorithm.dpll import solve


class DPLLTests(unittest.TestCase):
    def test_unit_propagation_and_complete_assignment(self):
        clauses = [[1], [-1, 2]]
        result = solve(clauses, 2)

        self.assertEqual(result.status, "SAT")
        self.assertEqual(set(result.assignment), {1, 2})
        self.assertTrue(result.assignment[1])
        self.assertTrue(result.assignment[2])
        self.assertGreaterEqual(result.stats.propagations, 2)

    def test_conflict_is_unsat(self):
        result = solve([[1], [-1]], 1)

        self.assertEqual(result.status, "UNSAT")
        self.assertIsNone(result.assignment)

    def test_empty_formula_is_sat(self):
        result = solve([], 3)

        self.assertEqual(result.status, "SAT")
        self.assertEqual(set(result.assignment), {1, 2, 3})

    def test_empty_clause_is_unsat(self):
        result = solve([[]], 3)

        self.assertEqual(result.status, "UNSAT")

    def test_deterministic_branching_backtracks(self):
        result = solve([[1, 2], [1, -2], [-1, 2], [-1, -2]], 2)

        self.assertEqual(result.status, "UNSAT")
        self.assertGreater(result.stats.decisions, 0)
        self.assertGreater(result.stats.backtracks, 0)

    def test_solver_does_not_mutate_input(self):
        clauses = [[1, 2], [-1]]
        before = [clause.copy() for clause in clauses]

        solve(clauses, 2)

        self.assertEqual(clauses, before)

    def test_invalid_literals_raise(self):
        with self.assertRaises(ValueError):
            solve([[0]], 2)
        with self.assertRaises(ValueError):
            solve([[3]], 2)
        with self.assertRaises(ValueError):
            solve([[True]], 2)


if __name__ == "__main__":
    unittest.main()
