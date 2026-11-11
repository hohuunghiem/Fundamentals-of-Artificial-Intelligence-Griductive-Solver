import unittest
from pathlib import Path

from algorithm.agent import LogicAgent
from controller import GameController
from engine import GameEngine


PUZZLES = Path(__file__).resolve().parents[1] / "puzzles"

LEVELS = [
    "demo_3x3.json",
    "demo_4x4.json",
    "level_3x3_medium_01.json",
    "level_3x3_medium_02.json",
    "level_4x4_medium.json",
    "level_4x4_hard.json",
    "level_5x5_medium.json",
    "level_5x5_medium_02.json",
    "level_5x5_hard.json",
]


class LogicAgentTests(unittest.TestCase):

    def test_c3_medium_01(self):
        engine = GameEngine(LogicAgent())
        state = engine.load_puzzle(
            PUZZLES / "level_3x3_medium_01.json"
        )

        result = engine.agent.classify(state, "C3")

        self.assertEqual(result.status, "CRIMINAL")

        submit = engine.submit_verdict("C3", "CRIMINAL")
        self.assertEqual(submit.status, "ACCEPTED")

    def test_all_levels_auto_solve(self):
        for filename in LEVELS:
            with self.subTest(level=filename):
                controller = GameController(
                    GameEngine(LogicAgent())
                )

                state = controller.load(PUZZLES / filename)
                total = state["size"] ** 2

                for _ in range(total):
                    current = (
                        controller.engine.get_public_state()
                    )

                    if len(current["known_statuses"]) == total:
                        break

                    move, result = controller.auto_step()

                    self.assertEqual(
                        move.status, "MOVE",
                        f"{filename}: {move.status}"
                    )

                    self.assertIsNotNone(result)
                    self.assertEqual(
                        result.status, "ACCEPTED"
                    )

                final_state = (
                    controller.engine.get_public_state()
                )

                self.assertEqual(
                    len(final_state["known_statuses"]),
                    total
                )

                self.assertEqual(
                    controller.hint().status,
                    "SOLVED"
                )


if __name__ == "__main__":
    unittest.main()
