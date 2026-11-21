"""Offline checks; full clues are never passed to the gameplay agent."""
from algorithm.agent import LogicAgent
from algorithm.encoder import encode
from algorithm.dpll import solve
from controller import GameController
from engine import GameEngine
from semantics import evaluate_clue


def check_uniqueness(puzzle: dict) -> str:
    kb = encode({"size": puzzle["size"], "known_statuses": {},
                 "revealed_clues": puzzle["clues"]})
    first = solve(kb.clauses, kb.num_vars)
    if first.status == "UNSAT":
        return "INCONSISTENT"
    blocking = [-v if first.assignment[v] else v for v in kb.cell_to_var.values()]
    second = solve(kb.clauses + [blocking], kb.num_vars)
    if second.status == "SAT":
        return "MULTIPLE"
    assignment = {cell: first.assignment[v] for cell, v in kb.cell_to_var.items()}
    if not all(evaluate_clue(c, assignment, puzzle["size"]) for c in puzzle["clues"]):
        raise ValueError("SAT assignment fails independent clue evaluation")
    if assignment != puzzle["solution"]:
        raise ValueError("Unique assignment does not match hidden solution")
    return "UNIQUE"


def check_progressive_solvability(puzzle: dict) -> dict:
    controller = GameController(GameEngine(LogicAgent()))
    controller.engine.load_data(puzzle)
    while True:
        move, result = controller.auto_step()
        if move.status != "MOVE":
            status = move.status
            break
        if result.status != "ACCEPTED":
            status = result.status
            break
    return {"status": status, "steps": controller.step, "trace": controller.trace,
            "public_state": controller.engine.get_public_state()}


def validate_puzzle(puzzle: dict) -> dict:
    """
    Perform a complete validation of a puzzle.
    """
    result = {
        "puzzle_id": puzzle.get("puzzle_id", "unknown"),
        "valid_structure": False,
        "uniqueness": "NOT_CHECKED",
        "solvability": "NOT_CHECKED",
        "steps": 0,
        "is_valid": False,
        "errors": []
    }

    try:
        GameEngine._validated_data(puzzle)
        result["valid_structure"] = True

    except (ValueError, TypeError, KeyError) as e:
        result["errors"].append(str(e))
        return result

    try:
        result["uniqueness"] = check_uniqueness(puzzle)

    except Exception as e:
        result["errors"].append(f"Uniqueness check failed: {e}")
        return result

    try:
        progress = check_progressive_solvability(puzzle)
        result["solvability"] = progress["status"]
        result["steps"] = progress["steps"]

    except Exception as e:
        result["errors"].append(f"Solvability check failed: {e}")
        return result

    result["is_valid"] = (
        result["valid_structure"]
        and result["uniqueness"] == "UNIQUE"
        and result["solvability"] == "SOLVED"
    )

    return result
