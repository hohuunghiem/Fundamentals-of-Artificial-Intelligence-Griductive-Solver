# Deductive Logic Agent (requirement 4.4)

The agent accepts public state only. `classify` checks KB consistency and
both temporary verdict assumptions using DPLL. An UNSAT opposite assumption
proves a verdict; two SAT assumptions mean UNKNOWN. `classify_all` returns
all unresolved characters in row-major order. `next_move` returns the first
forced verdict, or SOLVED, STUCK, or INCONSISTENT. Each call rebuilds the KB
from the current revealed clues and known verdicts.

`GameController.auto_step()` asks for a move and submits it to GameEngine.
Only an accepted verdict reveals a new clue. The next step uses the updated
public snapshot. `controller.trace` contains step, active clue IDs, cell,
verdict, newly revealed clue, and actual SAT queries from move selection and
engine verification. Each query records assumptions, SAT/UNSAT and solver
statistics. Relevant clue IDs are all active premises, not a minimal core.

Offline validation is separate:

```python
from algorithm.validator import check_uniqueness, check_progressive_solvability

uniqueness = check_uniqueness(puzzle_dict)
report = check_progressive_solvability(puzzle_dict)
```

Uniqueness encodes all clues without solution units, then blocks the first
model on primary variables only. It returns UNIQUE, MULTIPLE or INCONSISTENT.
A unique model is checked against the independent semantic evaluator and
hidden solution; a mismatch raises ValueError. Progressive validation uses
GameEngine and only public snapshots, returning status, steps, trace and
final public state. Unique full clues do not guarantee progressive solvability.

Known data issue: `demo_4x4.json` is MULTIPLE under the complete clue set
alone. Its initial revealed verdict disambiguates gameplay, so Auto Solve
still succeeds. The other eight bundled puzzles have UNIQUE complete clues.

This branch only changes requirement 4.4: agent, offline validator, its tests
and this document. Encoder (4.2), DPLL (4.3), shared models, engine, controller,
GUI, puzzle data and experiment runner are unchanged.

Integration requires the existing contracts:

- `encoder.encode(public_state) -> EncodedKB` with deterministic row-major
  `cell_to_var`, CNF `clauses` and `num_vars`.
- `dpll.solve(clauses, num_vars) -> SATResult` with SAT/UNSAT, a complete
  assignment for SAT, and `SATStats` (runtime in milliseconds).

Encoder and DPLL are currently placeholders in develop. The 4.4 contract
tests mock these dependencies; they do not establish end-to-end correctness.
The previously observed nine successful playthroughs and demo uniqueness
issue were obtained with temporary implementations, which were removed to
preserve the other team members' scope. Recheck them after integration.

Run from `Source/`:

```console
python -m unittest discover -s tests -v
python main.py --headless-smoke
python main.py
```

While waiting for 4.2/4.3, run only the independent 4.4 contract tests:

```console
python -m unittest tests.test_deduction -v
```

Full integration tests and gameplay will raise NotImplementedError until
the owners complete encoder and DPLL. No fallback solver is included.
