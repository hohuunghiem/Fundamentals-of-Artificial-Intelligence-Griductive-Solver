"""Shared geometric region utility (safe for Engine / GUI / future encoder).

Extension region kinds: CORNERS and COMMON_NEIGHBORS. All results row-major.
"""
from __future__ import annotations


def all_cells(size: int) -> list[str]:
    if type(size) is not int or not 3 <= size <= 5:
        raise ValueError("Board size must be 3, 4 or 5")
    return [f"{chr(65 + col)}{row}" for row in range(1, size + 1) for col in range(size)]


def _coord(cell: str, size: int) -> tuple[int, int]:
    if not isinstance(cell, str) or cell not in all_cells(size):
        raise ValueError(f"Unknown cell: {cell!r}")
    return int(cell[1:]), ord(cell[0]) - 65


def _neighbors(cell: str, size: int) -> set[str]:
    r, c = _coord(cell, size)
    return {
        f"{chr(65 + cc)}{rr}"
        for rr in range(max(1, r - 1), min(size, r + 1) + 1)
        for cc in range(max(0, c - 1), min(size - 1, c + 1) + 1)
        if rr != r or cc != c
    }


def resolve_region(region: dict, size: int) -> list[str]:
    """Validate a region and return its cells, without duplicates, row-major.

    Raising ValueError rather than silently fixing invalid puzzle data is intentional.
    """
    order = all_cells(size)
    if not isinstance(region, dict):
        raise ValueError("Region must be a JSON object")
    kind = region.get("kind")
    if kind == "ROW":
        idx = region.get("index")
        if type(idx) is not int or not 1 <= idx <= size:
            raise ValueError("ROW.index must be an integer within board")
        chosen = set(order[(idx - 1) * size : idx * size])
    elif kind == "COLUMN":
        label = region.get("label")
        if not isinstance(label, str) or len(label) != 1 or label not in "ABCDE"[:size]:
            raise ValueError("COLUMN.label is invalid")
        chosen = {cell for cell in order if cell.startswith(label)}
    elif kind == "NEIGHBORS":
        chosen = _neighbors(region.get("cell"), size)
    elif kind == "CELLS":
        cells = region.get("cells")
        if not isinstance(cells, list) or any(not isinstance(c, str) for c in cells):
            raise ValueError("CELLS.cells must be a list of cell IDs")
        if len(cells) != len(set(cells)):
            raise ValueError("CELLS.cells cannot contain duplicates")
        for cell in cells:
            _coord(cell, size)
        chosen = set(cells)
    elif kind == "CORNERS":
        chosen = {f"A1", f"{chr(64+size)}1", f"A{size}", f"{chr(64+size)}{size}"}
    elif kind == "COMMON_NEIGHBORS":
        cells = region.get("cells")
        if not isinstance(cells, list) or len(cells) != 2 or cells[0] == cells[1]:
            raise ValueError("COMMON_NEIGHBORS requires two distinct cells")
        chosen = _neighbors(cells[0], size) & _neighbors(cells[1], size)
    else:
        raise ValueError(f"Unsupported region kind: {kind!r}")
    return [cell for cell in order if cell in chosen]


def referenced_cells(clue: dict, size: int) -> list[str]:
    """Coordinates emphasized when selecting a PUBLIC clue in the GUI."""
    kind = clue.get("type")
    if kind == "FACT":
        cell = clue.get("cell")
        _coord(cell, size)
        return [cell]
    if kind in ("SAME", "DIFFERENT"):
        cells = clue.get("cells", [])
        return [cell for cell in all_cells(size) if cell in cells]
    if kind in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        return resolve_region(clue["region"], size)
    return []
