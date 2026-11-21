"""Generate report-ready charts and Markdown tables for Griductive Solver.

Run from Source/:
    python -m experiments.plot_results

Inputs:
    experiments/results/experiment_summary.csv
    experiments/results/experiment_size_summary.csv
    experiments/results/experiment_runs.csv

Outputs:
    experiments/results/figures/*.png
    experiments/results/report_results_tables.md
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(__file__).resolve().parent / "results"
FIGURE_DIR = RESULT_DIR / "figures"
PUZZLE_FILE = RESULT_DIR / "experiment_summary.csv"
SIZE_FILE = RESULT_DIR / "experiment_size_summary.csv"
RUNS_FILE = RESULT_DIR / "experiment_runs.csv"
SIZES = [3, 4, 5]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def numeric(row: dict, key: str) -> float | None:
    value = row.get(key)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def grouped_mean(rows: list[dict], column: str) -> dict[int, float]:
    result = {}
    for size in SIZES:
        values = [
            value for row in rows
            if int(row["size"]) == size
            and (value := numeric(row, column)) is not None
        ]
        if not values:
            raise ValueError(f"No values for {column} at board size {size}.")
        result[size] = sum(values) / len(values)
    return result


def derive_solvability(runs: list[dict]) -> dict[str, str]:
    """Derive per-puzzle solvability from the actual repeated-run records."""
    grouped: dict[str, list[str]] = {}
    for run in runs:
        puzzle_id = run.get("puzzle_id", "unknown")
        if run.get("status") == "COMPLETED":
            grouped.setdefault(puzzle_id, []).append(run.get("solvability", "UNKNOWN"))

    result = {}
    for puzzle_id, statuses in grouped.items():
        solved = sum(status == "SOLVED" for status in statuses)
        if solved == len(statuses) and statuses:
            result[puzzle_id] = f"SOLVED ({solved}/{len(statuses)})"
        elif solved:
            result[puzzle_id] = f"PARTIAL ({solved}/{len(statuses)})"
        else:
            result[puzzle_id] = "NOT SOLVED"
    return result


def save_bar_chart(labels, values, title, xlabel, ylabel, filename,
                   errors=None, rotate_labels=False):
    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.15), 5.5))
    positions = list(range(len(labels)))
    bars = ax.bar(positions, values, yerr=errors,
                  capsize=4 if errors is not None else 0)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=35 if rotate_labels else 0,
                       ha="right" if rotate_labels else "center",
                       fontsize=8 if rotate_labels else 10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        label = f"{value:.2f}" if abs(value) < 100 else f"{value:.0f}"
        ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Created: {filename}")


def create_size_charts(size_rows, puzzle_rows):
    labels = [f"{size}x{size}" for size in SIZES]
    metrics = [
        ("avg_runtime_ms", "Average Runtime by Board Size", "Runtime (ms)", "runtime_by_size.png"),
        ("avg_sat_calls", "Average SAT Calls by Board Size", "SAT calls", "sat_calls_by_size.png"),
        ("avg_deduction_steps", "Average Deduction Steps by Board Size", "Deduction steps", "deduction_steps_by_size.png"),
    ]
    for column, title, ylabel, filename in metrics:
        values = [float(row[column]) for row in size_rows]
        error_key = "stdev_" + column.removeprefix("avg_")
        errors = [float(row.get(error_key, 0) or 0) for row in size_rows]
        save_bar_chart(labels, values, title, "Board size", ylabel, filename, errors)

    clauses = grouped_mean(puzzle_rows, "cnf_clauses")
    save_bar_chart(labels, [clauses[size] for size in SIZES],
                   "Average CNF Clauses by Board Size", "Board size",
                   "CNF clauses", "cnf_clauses_by_size.png")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    width = 0.24
    x = list(range(len(SIZES)))
    metrics = [("Decisions", "avg_decisions"),
               ("Propagations", "avg_propagations"),
               ("Backtracks", "avg_backtracks")]
    for index, (label, column) in enumerate(metrics):
        values = [float(row[column]) for row in size_rows]
        positions = [position + (index - 1) * width for position in x]
        bars = ax.bar(positions, values, width, label=label)
        if any(values):
            ax.bar_label(bars, fmt="%.0f", padding=2, fontsize=8)
    ax.set_title("Average DPLL Statistics by Board Size")
    ax.set_xlabel("Board size")
    ax.set_ylabel("Average count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "dpll_statistics_by_size.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created: dpll_statistics_by_size.png")


def create_puzzle_charts(puzzle_rows):
    rows = sorted(puzzle_rows, key=lambda row: (int(row["size"]), row["puzzle_id"]))
    labels = [row["puzzle_id"].replace("_", "\n") for row in rows]
    metrics = [
        ("avg_runtime_ms", "stdev_runtime_ms", "Average Runtime by Puzzle", "Runtime (ms)", "runtime_by_puzzle.png"),
        ("avg_sat_calls", "stdev_sat_calls", "Average SAT Calls by Puzzle", "SAT calls", "sat_calls_by_puzzle.png"),
        ("avg_decisions", "stdev_decisions", "Average DPLL Decisions by Puzzle", "Decisions", "decisions_by_puzzle.png"),
        ("avg_propagations", "stdev_propagations", "Average Unit Propagations by Puzzle", "Propagations", "propagations_by_puzzle.png"),
    ]
    for value_key, error_key, title, ylabel, filename in metrics:
        values = [numeric(row, value_key) or 0.0 for row in rows]
        errors = [numeric(row, error_key) or 0.0 for row in rows]
        save_bar_chart(labels, values, title, "Puzzle", ylabel, filename,
                       errors=errors, rotate_labels=True)
    clauses = [numeric(row, "cnf_clauses") or 0.0 for row in rows]
    save_bar_chart(labels, clauses, "CNF Clauses by Puzzle", "Puzzle",
                   "CNF clauses", "cnf_clauses_by_puzzle.png",
                   rotate_labels=True)


def create_report_tables(size_rows, puzzle_rows, runs):
    solvability = derive_solvability(runs)
    lines = [
        "# Griductive Solver - Experimental Results", "",
        "## Results by board size", "",
        "| Metric | 3x3 | 4x4 | 5x5 |",
        "|---|---:|---:|---:|",
    ]
    size_metrics = [
        ("Average SAT calls", "avg_sat_calls"),
        ("Average decisions", "avg_decisions"),
        ("Average propagations", "avg_propagations"),
        ("Average backtracks", "avg_backtracks"),
        ("Average deduction steps", "avg_deduction_steps"),
        ("Average runtime (ms)", "avg_runtime_ms"),
    ]
    for label, column in size_metrics:
        values = [float(row[column]) for row in size_rows]
        lines.append(f"| {label} | " + " | ".join(f"{v:.2f}" for v in values) + " |")

    clauses = grouped_mean(puzzle_rows, "cnf_clauses")
    lines.append("| Average CNF clauses | " + " | ".join(f"{clauses[s]:.2f}" for s in SIZES) + " |")
    lines.extend([
        "", "## Results by individual puzzle", "",
        "| Puzzle | Size | Primary vars | Auxiliary vars | CNF clauses | SAT calls | Decisions | Propagations | Backtracks | Steps | Runtime (ms) | Uniqueness | Solvability |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in sorted(puzzle_rows, key=lambda item: (int(item["size"]), item["puzzle_id"])):
        def fmt(key):
            value = numeric(row, key)
            return "N/A" if value is None else f"{value:.2f}"
        puzzle_id = row["puzzle_id"]
        lines.append(
            f"| {puzzle_id} | {row['size']} | {fmt('primary_variables')} | "
            f"{fmt('auxiliary_variables')} | {fmt('cnf_clauses')} | {fmt('avg_sat_calls')} | "
            f"{fmt('avg_decisions')} | {fmt('avg_propagations')} | {fmt('avg_backtracks')} | "
            f"{fmt('avg_deduction_steps')} | {fmt('avg_runtime_ms')} | "
            f"{row.get('uniqueness', 'N/A')} | {solvability.get(puzzle_id, 'NO RUN DATA')} |"
        )
    output = RESULT_DIR / "report_results_tables.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Created: report_results_tables.md")


def main():
    size_rows = read_csv(SIZE_FILE)
    puzzle_rows = read_csv(PUZZLE_FILE)
    runs = read_csv(RUNS_FILE)
    if len(size_rows) != 3:
        raise ValueError(f"Expected 3 size-summary rows; found {len(size_rows)}.")
    if not puzzle_rows:
        raise ValueError("The per-puzzle summary CSV is empty.")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    create_size_charts(size_rows, puzzle_rows)
    create_puzzle_charts(puzzle_rows)
    create_report_tables(size_rows, puzzle_rows, runs)
    print("\nAll report charts and tables generated successfully.")
    print(f"Figures: {FIGURE_DIR}")
    print(f"Tables: {RESULT_DIR / 'report_results_tables.md'}")


if __name__ == "__main__":
    main()
