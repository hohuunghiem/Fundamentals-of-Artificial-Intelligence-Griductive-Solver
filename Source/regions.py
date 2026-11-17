"""Region resolver: đổi mô tả vùng (dict) thành danh sách mã ô theo thứ tự hàng."""

COLS = "ABCDE"


def all_cells(size):
    """Mọi ô theo thứ tự hàng: A1, B1, C1, A2, ..."""
    return [f"{COLS[c]}{r}" for r in range(1, size + 1) for c in range(size)]


def parse_cell(cell, size):
    """'B2' -> (row=2, col=2). Báo lỗi nếu ô không tồn tại."""
    if not isinstance(cell, str) or len(cell) < 2:
        raise ValueError(f"Mã ô không hợp lệ: {cell!r}")
    col = COLS.find(cell[0]) + 1
    if col == 0 or col > size or not cell[1:].isdigit():
        raise ValueError(f"Mã ô không hợp lệ: {cell!r}")
    row = int(cell[1:])
    if not 1 <= row <= size:
        raise ValueError(f"Mã ô không hợp lệ: {cell!r}")
    return row, col


def neighbors(cell, size):
    """8 ô xung quanh (ngang, dọc, chéo), không gồm chính nó."""
    r, c = parse_cell(cell, size)
    out = set()
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (dr, dc) != (0, 0) and 1 <= r + dr <= size and 1 <= c + dc <= size:
                out.add(f"{COLS[c + dc - 1]}{r + dr}")
    return out


def resolve_region(region, size):
    kind = region.get("kind")
    if kind == "ROW":
        i = region.get("index")
        if not isinstance(i, int) or isinstance(i, bool) or not 1 <= i <= size:
            raise ValueError(f"ROW index không hợp lệ: {i!r}")
        chosen = {f"{COLS[c]}{i}" for c in range(size)}
    elif kind == "COLUMN":
        lab = region.get("label")
        if not isinstance(lab, str) or len(lab) != 1 or lab not in COLS[:size]:
            raise ValueError(f"COLUMN label không hợp lệ: {lab!r}")
        chosen = {f"{lab}{r}" for r in range(1, size + 1)}
    elif kind == "NEIGHBORS":
        chosen = neighbors(region.get("cell"), size)
    elif kind == "CELLS":
        cells = region.get("cells")
        if not isinstance(cells, list):
            raise ValueError("CELLS cần một list")
        for x in cells:
            parse_cell(x, size)
        if len(set(cells)) != len(cells):
            raise ValueError(f"CELLS bị trùng: {cells}")
        chosen = set(cells)
    elif kind == "CORNERS":                      # mở rộng 1
        last = COLS[size - 1]
        chosen = {"A1", f"{last}1", f"A{size}", f"{last}{size}"}
    elif kind == "COMMON_NEIGHBORS":             # mở rộng 2
        cells = region.get("cells")
        if not isinstance(cells, list) or len(cells) != 2 or cells[0] == cells[1]:
            raise ValueError("COMMON_NEIGHBORS cần đúng 2 ô khác nhau")
        chosen = neighbors(cells[0], size) & neighbors(cells[1], size)
    else:
        raise ValueError(f"Loại vùng không hỗ trợ: {kind!r}")
    return [c for c in all_cells(size) if c in chosen]   # sắp theo thứ tự hàng
