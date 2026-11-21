"""Griductive Solver - repeated experiments.

Run from the Source directory:
    python -m experiments.run_experiments

Each puzzle is solved REPEAT_COUNT times. The runner records every run,
per-puzzle statistics, and aggregates by board size.

Outputs (under experiments/results/):
    experiment_runs.csv
    experiment_summary.csv
    experiment_size_summary.csv
    experiment_results.json
"""

from __future__ import annotations

import csv
import json
import signal
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from algorithm import agent as agent_module
from algorithm.agent import LogicAgent
from algorithm.encoder import encode
from algorithm.validator import check_uniqueness
from controller import GameController
from engine import GameEngine


ROOT = Path(__file__).resolve().parents[1]
PUZZLE_DIR = ROOT / "puzzles"
RESULT_DIR = Path(__file__).resolve().parent / "results"

REPEAT_COUNT = 5
TIMEOUT_SECONDS = 30

METRICS = (
    "sat_calls",
    "decisions",
    "propagations",
    "backtracks",
    "deduction_steps",
    "runtime_ms",
)


class ExperimentTimeout(Exception):
    """Raised when one experiment exceeds its time limit."""


def _timeout_handler(signum: int, frame: Any) -> None:
    raise ExperimentTimeout(
        f"Experiment exceeded {TIMEOUT_SECONDS} seconds"
    )


def load_puzzle(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def measure_encoding(puzzle: dict) -> dict:
    """Measure CNF sizes for the full clue set and initial public state."""
    size = puzzle["size"]

    full_kb = encode({
        "size": size,
        "known_statuses": {},
        "revealed_clues": puzzle["clues"],
    })

    # Use the real engine to obtain exactly the initial public knowledge base.
    engine = GameEngine(LogicAgent())
    initial_state = engine.load_data(puzzle)
    initial_kb = encode(initial_state)

    return {
        "primary_variables": full_kb.primary_count,
        "auxiliary_variables": full_kb.aux_count,
        "cnf_clauses": full_kb.clause_count,
        "initial_cnf_clauses": initial_kb.clause_count,
    }


def run_once(puzzle: dict) -> dict:
    """Run one fresh game and collect all DPLL calls made by the agent."""
    size = puzzle["size"]
    engine = GameEngine(LogicAgent())
    engine.load_data(puzzle)
    controller = GameController(engine)

    totals = {
        "sat_calls": 0,
        "decisions": 0,
        "propagations": 0,
        "backtracks": 0,
    }

    # agent.py imports solve into its own module namespace. Instrument that
    # reference so every actual SAT query made by LogicAgent is counted once.
    original_solve = agent_module.solve

    def tracked_solve(clauses, num_vars):
        sat_result = original_solve(clauses, num_vars)
        totals["sat_calls"] += 1
        totals["decisions"] += sat_result.stats.decisions
        totals["propagations"] += sat_result.stats.propagations
        totals["backtracks"] += sat_result.stats.backtracks
        return sat_result

    terminal_status = "STEP_LIMIT"
    agent_module.solve = tracked_solve
    started = time.perf_counter()

    try:
        # At most size*size cards can be revealed. One extra iteration lets
        # the agent report SOLVED after the final successful reveal.
        for _ in range(size * size + 1):
            move, submit_result = controller.auto_step()

            if move.status != "MOVE":
                terminal_status = move.status
                break

            if submit_result is None:
                terminal_status = "ERROR"
                break

            if submit_result.status != "ACCEPTED":
                terminal_status = submit_result.status
                break
        else:
            terminal_status = "STEP_LIMIT"

        runtime_ms = (time.perf_counter() - started) * 1000.0
    finally:
        # Always restore the original solver, including on timeout/error.
        agent_module.solve = original_solve

    return {
        **totals,
        "deduction_steps": controller.step,
        "runtime_ms": runtime_ms,
        "solvability": terminal_status,
    }


def run_with_timeout(puzzle: dict) -> dict:
    """Run one experiment with a Unix alarm timeout (Linux/Ubuntu)."""
    if not hasattr(signal, "SIGALRM"):
        raise RuntimeError("This timeout implementation requires Unix SIGALRM")

    previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)
    try:
        return run_once(puzzle)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def safe_stdev(values: list[float]) -> float:
    # Sample standard deviation; zero when fewer than two runs completed.
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def summarize_runs(
    puzzle_id: str,
    size: int,
    runs: list[dict],
    uniqueness: str,
    encoding: dict,
) -> dict:
    """Aggregate completed runs while explicitly retaining failure counts."""
    completed = [run for run in runs if run.get("status") == "COMPLETED"]

    summary = {
        "puzzle_id": puzzle_id,
        "size": size,
        **encoding,
        "repeat_count": REPEAT_COUNT,
        "completed_runs": len(completed),
        "timeouts": sum(run.get("status") == "TIMEOUT" for run in runs),
        "errors": sum(run.get("status") == "ERROR" for run in runs),
        "uniqueness": uniqueness,
        "solved_runs": sum(
            run.get("solvability") == "SOLVED" for run in completed
        ),
        "failed_solving_runs": sum(
            run.get("solvability") != "SOLVED" for run in completed
        ),
    }

    for metric in METRICS:
        values = [run[metric] for run in completed if metric in run]
        summary[f"avg_{metric}"] = safe_mean(values)
        summary[f"stdev_{metric}"] = safe_stdev(values)

    summary["overall_status"] = (
        "SUCCESS"
        if uniqueness == "UNIQUE"
        and summary["solved_runs"] == REPEAT_COUNT
        and summary["timeouts"] == 0
        and summary["errors"] == 0
        else "INVALID_OR_INCOMPLETE"
    )
    return summary


def process_puzzle(path: Path) -> tuple[list[dict], dict]:
    """Validate/encode once, then run the puzzle REPEAT_COUNT times."""
    puzzle = load_puzzle(path)
    puzzle_id = puzzle.get("puzzle_id", path.stem)
    size = puzzle.get("size")

    print("\n" + "=" * 65)
    print(f"PUZZLE: {puzzle_id}")
    print("=" * 65)

    try:
        encoding = measure_encoding(puzzle)
        uniqueness = check_uniqueness(puzzle)
    except Exception as error:
        message = f"{type(error).__name__}: {error}"
        error_runs = [{
            "puzzle_id": puzzle_id,
            "size": size,
            "repeat": 0,
            "status": "ERROR",
            "error": f"Pre-check failed: {message}",
        }]
        error_summary = {
            "puzzle_id": puzzle_id,
            "size": size,
            "repeat_count": REPEAT_COUNT,
            "completed_runs": 0,
            "timeouts": 0,
            "errors": 1,
            "uniqueness": "NOT_CHECKED",
            "solved_runs": 0,
            "failed_solving_runs": 0,
            "overall_status": "ERROR",
            "error": message,
        }
        return error_runs, error_summary

    runs = []
    for repeat in range(1, REPEAT_COUNT + 1):
        print(f"Run {repeat}/{REPEAT_COUNT}...", end=" ", flush=True)
        record = {
            "puzzle_id": puzzle_id,
            "size": size,
            "repeat": repeat,
            **encoding,
            "uniqueness": uniqueness,
        }

        try:
            result = run_with_timeout(puzzle)
            record.update(result)
            record["status"] = "COMPLETED"
            record["error"] = ""
            print(f"{result['solvability']} | {result['runtime_ms']:.3f} ms")
        except ExperimentTimeout as error:
            record.update({"status": "TIMEOUT", "error": str(error)})
            print("TIMEOUT")
        except Exception as error:
            record.update({
                "status": "ERROR",
                "error": f"{type(error).__name__}: {error}",
            })
            print(f"ERROR: {error}")

        runs.append(record)

    summary = summarize_runs(puzzle_id, size, runs, uniqueness, encoding)
    return runs, summary


def summarize_by_size(all_runs: list[dict], summaries: list[dict]) -> list[dict]:
    """Aggregate completed run-level measurements by board size."""
    grouped: dict[int, list[dict]] = defaultdict(list)
    for run in all_runs:
        if run.get("status") == "COMPLETED":
            grouped[run["size"]].append(run)

    puzzle_counts: dict[int, int] = defaultdict(int)
    for summary in summaries:
        if isinstance(summary.get("size"), int):
            puzzle_counts[summary["size"]] += 1

    size_rows = []
    for size in sorted(set(puzzle_counts) | set(grouped)):
        runs = grouped[size]
        row = {
            "size": size,
            "puzzle_count": puzzle_counts[size],
            "completed_runs": len(runs),
            "timeouts": sum(
                run.get("status") == "TIMEOUT" and run.get("size") == size
                for run in all_runs
            ),
            "errors": sum(
                run.get("status") == "ERROR" and run.get("size") == size
                for run in all_runs
            ),
        }
        for metric in METRICS:
            values = [run[metric] for run in runs if metric in run]
            row[f"avg_{metric}"] = safe_mean(values)
            row[f"stdev_{metric}"] = safe_stdev(values)
        size_rows.append(row)

    return size_rows


def save_csv(path: Path, records: list[dict]) -> None:
    if not records:
        return

    fields = list(dict.fromkeys(
        key for record in records for key in record
    ))
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(records)


def save_results(
    all_runs: list[dict],
    summaries: list[dict],
    size_summaries: list[dict],
) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    save_csv(RESULT_DIR / "experiment_runs.csv", all_runs)
    save_csv(RESULT_DIR / "experiment_summary.csv", summaries)
    save_csv(RESULT_DIR / "experiment_size_summary.csv", size_summaries)

    json_path = RESULT_DIR / "experiment_results.json"
    payload = {
        "configuration": {
            "repeat_count": REPEAT_COUNT,
            "timeout_seconds": TIMEOUT_SECONDS,
            "runtime_unit": "milliseconds",
            "standard_deviation": "sample standard deviation",
            "summary_average_population": "completed runs only; failures are counted separately",
        },
        "runs": all_runs,
        "puzzle_summaries": summaries,
        "size_summaries": size_summaries,
    }
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)

    print("\nSaved results:")
    print(RESULT_DIR / "experiment_runs.csv")
    print(RESULT_DIR / "experiment_summary.csv")
    print(RESULT_DIR / "experiment_size_summary.csv")
    print(json_path)


def main() -> None:
    puzzle_files = sorted(PUZZLE_DIR.glob("*.json"))
    if not puzzle_files:
        print(f"No puzzle JSON files found in {PUZZLE_DIR}")
        return

    print("=" * 65)
    print("GRIDUCTIVE SOLVER - REPEATED EXPERIMENTS")
    print(f"Repetitions per puzzle: {REPEAT_COUNT}")
    print(f"Timeout per run: {TIMEOUT_SECONDS} seconds")
    print(f"Number of puzzles: {len(puzzle_files)}")
    print("=" * 65)

    all_runs: list[dict] = []
    summaries: list[dict] = []

    for index, path in enumerate(puzzle_files, start=1):
        print(f"\nPuzzle {index}/{len(puzzle_files)}: {path.name}")
        try:
            runs, summary = process_puzzle(path)
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            runs = [{
                "puzzle_id": path.stem,
                "repeat": 0,
                "status": "ERROR",
                "error": message,
            }]
            summary = {
                "puzzle_id": path.stem,
                "repeat_count": REPEAT_COUNT,
                "completed_runs": 0,
                "timeouts": 0,
                "errors": 1,
                "uniqueness": "NOT_CHECKED",
                "solved_runs": 0,
                "failed_solving_runs": 0,
                "overall_status": "ERROR",
                "error": message,
            }

        all_runs.extend(runs)
        summaries.append(summary)

    size_summaries = summarize_by_size(all_runs, summaries)
    save_results(all_runs, summaries, size_summaries)

    print("\n" + "=" * 65)
    print("FINAL EXPERIMENT SUMMARY")
    print("=" * 65)
    print("Total puzzles:", len(summaries))
    print("Total experiment records:", len(all_runs))
    print("Completed runs:", sum(s.get("completed_runs", 0) for s in summaries))
    print("Timeouts:", sum(s.get("timeouts", 0) for s in summaries))
    print("Errors:", sum(s.get("errors", 0) for s in summaries))


if __name__ == "__main__":
    main()
