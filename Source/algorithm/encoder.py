"""CNF encoder: đổi manh mối công khai thành CNF dạng list[list[int]]."""

from itertools import combinations

from models import EncodedKB
from regions import all_cells, parse_cell
from semantics import _two_cells, _region_and_k


def build_var_map(size):
    """var_id = (row - 1) * size + column_index  (A1=1, B1=2, ...)."""
    return {cell: i + 1 for i, cell in enumerate(all_cells(size))}


def at_most(vars_, k):
    """Mỗi tập con k+1 biến: không thể tất cả đều True."""
    _validate_count(vars_, k)
    return [[-v for v in combo] for combo in combinations(vars_, k + 1)]


def at_least(vars_, k):
    """Mỗi tập con n-k+1 biến: phải có ít nhất 1 True."""
    _validate_count(vars_, k)
    if k == 0:
        return []
    return [list(combo) for combo in combinations(vars_, len(vars_) - k + 1)]


def _validate_count(vars_, k):
    if type(k) is not int or not 0 <= k <= len(vars_):
        raise ValueError("k must be an integer between 0 and the region size")


def encode_clue(clue, size, var):
    if not isinstance(clue, dict):
        raise ValueError("Clue must be a dictionary")
    if var != build_var_map(size):
        raise ValueError("Variable mapping must match the board in row-major order")
    t = clue.get("type")

    if t == "FACT":
        parse_cell(clue.get("cell"), size)
        if not isinstance(clue.get("criminal"), bool):
            raise ValueError(f"{clue.get('id')}: 'criminal' phải là true/false")
        i = var[clue["cell"]]
        return [[i]] if clue["criminal"] else [[-i]]

    if t == "SAME":
        a, b = (var[c] for c in _two_cells(clue, size))
        return [[-a, b], [a, -b]]

    if t == "DIFFERENT":
        a, b = (var[c] for c in _two_cells(clue, size))
        return [[a, b], [-a, -b]]

    if t in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        region, k = _region_and_k(clue, size)
        vs = [var[c] for c in region]
        if t == "AT_MOST":
            return at_most(vs, k)
        if t == "AT_LEAST":
            return at_least(vs, k)
        return at_most(vs, k) + at_least(vs, k)

    raise ValueError(f"Loại manh mối không hỗ trợ: {t!r}")


def encode(public_state):
    """KB_t = CNF(manh mối đã mở) ∧ unit clause của trạng thái đã biết."""
    if not isinstance(public_state, dict):
        raise ValueError("Public state must be a dictionary")
    size = public_state.get("size")
    var = build_var_map(size)
    clues = public_state.get("revealed_clues")
    known = public_state.get("known_statuses")
    if not isinstance(clues, list) or not isinstance(known, dict):
        raise ValueError("Public state requires revealed_clues list and known_statuses dictionary")
    clauses = []

    for clue in clues:
        clauses.extend(encode_clue(clue, size, var))

    for cell, criminal in known.items():
        parse_cell(cell, size)
        if type(criminal) is not bool:
            raise ValueError("Known verdicts must be boolean")
        clauses.append([var[cell]] if criminal else [-var[cell]])

    primary = size * size
    return EncodedKB(
        clauses=clauses,
        cell_to_var=var,
        primary_count=primary,
        aux_count=0,
        num_vars=primary,
        clause_count=len(clauses),
    )
