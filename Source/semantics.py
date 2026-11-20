"""Semantic evaluator: kiểm tra trực tiếp một manh mối trên phép gán đầy đủ.
KHÔNG gọi encoder — dùng để đối chiếu với CNF và kiểm tra dữ liệu màn."""

from regions import all_cells, resolve_region, parse_cell

COUNT_TYPES = ("EXACTLY", "AT_LEAST", "AT_MOST")


def _size(board):
    """board có thể là số (size) hoặc dict có khóa 'size'."""
    size = board.get("size") if isinstance(board, dict) else board
    all_cells(size)
    return size


def _two_cells(clue, size):
    if not isinstance(clue, dict):
        raise ValueError("Clue must be a dictionary")
    cells = clue.get("cells")
    if not isinstance(cells, list) or len(cells) != 2 or cells[0] == cells[1]:
        raise ValueError(f"{clue.get('id')}: cần đúng 2 ô khác nhau")
    for x in cells:
        parse_cell(x, size)
    return cells


def _region_and_k(clue, size):
    if not isinstance(clue, dict):
        raise ValueError("Clue must be a dictionary")
    region = resolve_region(clue.get("region", {}), size)
    k = clue.get("k")
    if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k <= len(region):
        raise ValueError(f"{clue.get('id')}: k={k!r} không hợp lệ với vùng {len(region)} ô")
    return region, k


def _validate_content(clue, size):
    """Validate logical content independently of puzzle metadata."""
    all_cells(size)
    if not isinstance(clue, dict):
        raise ValueError("Clue must be a dictionary")
    t = clue.get("type")
    if t == "FACT":
        parse_cell(clue.get("cell"), size)
        if type(clue.get("criminal")) is not bool:
            raise ValueError(f"{clue.get('id')}: 'criminal' phải là true/false")
    elif t in ("SAME", "DIFFERENT"):
        _two_cells(clue, size)
    elif t in COUNT_TYPES:
        _region_and_k(clue, size)
    else:
        raise ValueError(f"Unsupported clue type: {t!r}")


def validate_clue(clue, size):
    """Validate a puzzle clue, including its ID and owner, for GameEngine."""
    _validate_content(clue, size)
    if not isinstance(clue.get("id"), str) or not clue["id"].strip():
        raise ValueError("Clue must have a nonempty id")
    parse_cell(clue.get("owner"), size)


def evaluate_clue(clue, assignment, board):
    """assignment: dict mã ô -> bool (True = Criminal), đủ mọi ô.

    Logical evaluation also accepts standalone clues without owner/id metadata.
    """
    size = _size(board)
    _validate_content(clue, size)
    if not isinstance(assignment, dict) or set(assignment) != set(all_cells(size)):
        raise ValueError("Assignment must cover every board cell exactly once")
    if any(type(value) is not bool for value in assignment.values()):
        raise ValueError("Assignment values must be boolean")
    t = clue["type"]
    if t == "FACT":
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
