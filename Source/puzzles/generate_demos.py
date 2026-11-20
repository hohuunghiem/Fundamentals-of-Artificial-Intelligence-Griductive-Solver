"""Only for creating simple integration fixtures. Not a solver/puzzle generator.

All examples are deliberately easy FACT chains, NOT benchmark cases.
Run from Source/: python puzzles/generate_demos.py
"""
from __future__ import annotations

import json
from pathlib import Path


def make(size: int, names: list[str], statuses: list[bool]) -> dict:
    cells = [f"{chr(65+c)}{r}" for r in range(1, size+1) for c in range(size)]
    professions = ["Thám tử", "Bác sĩ", "Giáo viên", "Kỹ sư", "Đầu bếp",
                   "Luật sư", "Nghệ sĩ", "Kiến trúc sư", "Nhà báo", "Phi công",
                   "Nhà khoa học", "Thủ thư", "Y tá", "Nhà thiết kế", "Vận động viên", "Họa sĩ"]
    solution = dict(zip(cells, statuses))
    clues = [{"id": f"clue_{cell}", "owner": cell, "type": "FACT",
              "cell": cells[i+1], "criminal": statuses[i+1]}
             for i, cell in enumerate(cells[:-1])]
    if size == 3:
        corners = (cells[0], cells[size-1], cells[-size], cells[-1])
        clues.append({"id": f"clue_{cells[-1]}", "owner": cells[-1], "type": "EXACTLY",
                      "k": sum(solution[c] for c in corners), "region": {"kind": "CORNERS"}})
    else:
        # A small worked example of advanced common-neighbors region.
        group = [f"{chr(65+c)}{r}" for r in range(1, size+1) for c in range(size)
                 if all(abs(r-rr) <= 1 and abs(c-cc) <= 1 and (r, c) != (rr, cc)
                        for rr, cc in ((2, 1), (2, 2)))]
        clues.append({"id": f"clue_{cells[-1]}", "owner": cells[-1], "type": "AT_MOST",
                      "k": sum(solution[c] for c in group),
                      "region": {"kind": "COMMON_NEIGHBORS", "cells": ["B2", "C2"]}})
    return {
        "schema_version": 1,
        "puzzle_id": f"demo_{size}x{size}_fact_chain",
        "size": size,
        "characters": [{"cell": c, "name": name, "profession": professions[i]}
                       for i, (c, name) in enumerate(zip(cells, names))],
        "solution": solution,
        "clues": clues,
        "initial_revealed": [cells[0]],
    }


if __name__ == "__main__":
    out = Path(__file__).resolve().parent
    specs = (
        (3, ["An", "Binh", "Chi", "Dung", "Giang", "Ha", "Khoa", "Lan", "Minh"],
         [False, True, True, False, False, True, False, True, False]),
        (4, ["An", "Bach", "Chi", "Dung", "Giang", "Ha", "Hieu", "Khanh",
             "Lan", "Linh", "Minh", "Nam", "Oanh", "Phuc", "Quang", "Trang"],
         [True, False, True, False, True, False, False, True,
          True, False, True, False, False, True, False, True]),
    )
    for size, names, statuses in specs:
        path = out / f"demo_{size}x{size}.json"
        path.write_text(json.dumps(make(size, names, statuses), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Created", path)
