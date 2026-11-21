# Griductive Solver - Experimental Results

## Results by board size

| Metric | 3x3 | 4x4 | 5x5 |
|---|---:|---:|---:|
| Average SAT calls | 53.67 | 107.00 | 226.33 |
| Average decisions | 101.33 | 436.67 | 1648.00 |
| Average propagations | 343.67 | 1116.67 | 3649.00 |
| Average backtracks | 0.00 | 0.00 | 0.00 |
| Average deduction steps | 7.33 | 14.00 | 22.33 |
| Average runtime (ms) | 8.08 | 26.95 | 115.95 |
| Average CNF clauses | 39.33 | 75.00 | 264.33 |

## Results by individual puzzle

| Puzzle | Size | Primary vars | Auxiliary vars | CNF clauses | SAT calls | Decisions | Propagations | Backtracks | Steps | Runtime (ms) | Uniqueness | Solvability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| demo_3x3_fact_chain | 3 | 9.00 | 0.00 | 15.00 | 49.00 | 112.00 | 273.00 | 0.00 | 8.00 | 5.76 | UNIQUE | SOLVED (5/5) |
| level_3x3_medium_01 | 3 | 9.00 | 0.00 | 57.00 | 59.00 | 102.00 | 401.00 | 0.00 | 7.00 | 9.13 | UNIQUE | SOLVED (5/5) |
| level_3x3_medium_02 | 3 | 9.00 | 0.00 | 46.00 | 53.00 | 90.00 | 357.00 | 0.00 | 7.00 | 9.35 | UNIQUE | SOLVED (5/5) |
| demo_4x4_fact_chain | 4 | 16.00 | 0.00 | 19.00 | 91.00 | 420.00 | 826.00 | 0.00 | 15.00 | 17.04 | MULTIPLE | SOLVED (5/5) |
| level_4x4_hard | 4 | 16.00 | 0.00 | 88.00 | 143.00 | 670.00 | 1462.00 | 0.00 | 14.00 | 36.26 | UNIQUE | SOLVED (5/5) |
| level_4x4_medium | 4 | 16.00 | 0.00 | 118.00 | 87.00 | 220.00 | 1062.00 | 0.00 | 13.00 | 27.53 | UNIQUE | SOLVED (5/5) |
| level_5x5_hard | 5 | 25.00 | 0.00 | 357.00 | 283.00 | 2420.00 | 4279.00 | 0.00 | 23.00 | 137.71 | UNIQUE | SOLVED (5/5) |
| level_5x5_medium | 5 | 25.00 | 0.00 | 203.00 | 167.00 | 822.00 | 3047.00 | 0.00 | 22.00 | 88.26 | UNIQUE | SOLVED (5/5) |
| level_5x5_medium_02 | 5 | 25.00 | 0.00 | 233.00 | 229.00 | 1702.00 | 3621.00 | 0.00 | 22.00 | 121.89 | UNIQUE | SOLVED (5/5) |
