"""Griductive Project 2 entrypoint; Python 3.10+, Tkinter standard library."""
from __future__ import annotations

import argparse
from pathlib import Path

from algorithm.agent import LogicAgent
from controller import GameController
from engine import GameEngine

HERE = Path(__file__).resolve().parent
DEFAULT_PUZZLE = HERE / "puzzles" / "demo_3x3.json"


def main():
    parser = argparse.ArgumentParser(description="Griductive - no-guess deduction game")
    parser.add_argument("--puzzle", type=Path, default=DEFAULT_PUZZLE)
    parser.add_argument("--headless-smoke", action="store_true",
                        help="Run the demonstration agent without GUI")
    args = parser.parse_args()
    logic_agent = LogicAgent()
    controller = GameController(GameEngine(logic_agent))
    if args.headless_smoke:
        state = controller.load(args.puzzle)
        print(f"Loaded: {state['puzzle_id']} ({state['size']}x{state['size']})")
        max_steps = state["size"] ** 2
        for _ in range(max_steps):
            move, result = controller.auto_step()
            if result is None:
                print(f"Stopped: {move.status}")
                break
            print(f"{move.cell}: {move.verdict} -> {result.status}")
            if result.status != "ACCEPTED":
                break
        print(f"Revealed: {len(controller.engine.get_public_state()['known_statuses'])}")
        return
    import tkinter as tk
    from gui.menu import GameNavigator

    root = tk.Tk()

    navigator = GameNavigator(
        root,
        controller
    )

    # Vẫn hỗ trợ mở trực tiếp một puzzle từ dòng lệnh
    if args.puzzle.resolve() != DEFAULT_PUZZLE.resolve():
        navigator.open_level(args.puzzle)

    root.mainloop()


if __name__ == "__main__":
    main()
