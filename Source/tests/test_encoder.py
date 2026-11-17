"""So CNF với semantic evaluator trên MỌI phép gán (brute force)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from itertools import product
from encoder import encode_clue, build_var_map, encode
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

for clue in clues:
    cnf = encode_clue(clue, SIZE, VAR)
    for bits in product([False, True], repeat=len(CELLS)):
        a = dict(zip(CELLS, bits))
        assert cnf_true(cnf, a) == evaluate_clue(clue, a, SIZE), (clue, a)
print(f"OK: {len(clues)} manh mối x 512 phép gán đều khớp")

bad = [
    {"id": "b1", "type": "EXACTLY", "k": 4, "region": {"kind": "ROW", "index": 1}},
    {"id": "b2", "type": "EXACTLY", "k": True, "region": {"kind": "ROW", "index": 1}},
    {"id": "b3", "type": "SAME", "cells": ["A1", "A1"]},
    {"id": "b4", "type": "FACT", "cell": "D1", "criminal": True},
]
for clue in bad:
    try:
        encode_clue(clue, SIZE, VAR)
        raise SystemExit(f"Thiếu báo lỗi: {clue}")
    except ValueError:
        pass
print("OK: dữ liệu sai đều bị báo lỗi")
