"""Semantic evaluator: kiểm tra trực tiếp một manh mối trên phép gán đầy đủ.
KHÔNG gọi encoder — dùng để đối chiếu với CNF và kiểm tra dữ liệu màn."""

from regions import resolve_region, parse_cell

COUNT_TYPES = ("EXACTLY", "AT_LEAST", "AT_MOST")


def _size(board):
    """board có thể là số (size) hoặc dict có khóa 'size'."""
    return board["size"] if isinstance(board, dict) else board


def _two_cells(clue, size):
    cells = clue.get("cells")
    if not isinstance(cells, list) or len(cells) != 2 or cells[0] == cells[1]:
        raise ValueError(f"{clue.get('id')}: cần đúng 2 ô khác nhau")
    for x in cells:
        parse_cell(x, size)
    return cells


def _region_and_k(clue, size):
    region = resolve_region(clue.get("region", {}), size)
    k = clue.get("k")
    if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k <= len(region):
        raise ValueError(f"{clue.get('id')}: k={k!r} không hợp lệ với vùng {len(region)} ô")
    return region, k


def evaluate_clue(clue, assignment, board):
    """assignment: dict mã ô -> bool (True = Criminal), đủ mọi ô."""
    size = _size(board)
    t = clue.get("type")

    if t == "FACT":
        parse_cell(clue.get("cell"), size)
        if not isinstance(clue.get("criminal"), bool):
            raise ValueError(f"{clue.get('id')}: 'criminal' phải là true/false")
        return assignment[clue["cell"]] == clue["criminal"]

    if t in ("SAME", "DIFFERENT"):
        a, b = _two_cells(clue, size)
        same = assignment[a] == assignment[b]
        return same if t == "SAME" else not same

    if t in COUNT_TYPES:
        region, k = _region_and_k(clue, size)
        count = sum(1 for c in region if assignment[c])
        if t == "EXACTLY":
            return count == k
        if t == "AT_LEAST":
            return count >= k
        return count <= k

    raise ValueError(f"Loại manh mối không hỗ trợ: {t!r}")
