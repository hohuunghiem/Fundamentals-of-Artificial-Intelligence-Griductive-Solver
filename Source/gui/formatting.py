"""Presentation-only clue language; no NLP or solver dependencies."""
from __future__ import annotations


def region_text(region: dict) -> str:
    kind = region.get("kind")
    if kind == "ROW":
        return f"hàng {region['index']}"
    if kind == "COLUMN":
        return f"cột {region['label']}"
    if kind == "NEIGHBORS":
        return f"các ô kề {region['cell']} (kể cả đường chéo)"
    if kind == "CELLS":
        return "nhóm " + ", ".join(region["cells"])
    if kind == "CORNERS":
        return "bốn góc của bàn cờ"
    if kind == "COMMON_NEIGHBORS":
        return "các ô kề chung của " + " và ".join(region["cells"])
    return str(region)


def clue_text(clue: dict) -> str:
    kind = clue.get("type")
    if kind == "FACT":
        status = "TỘI PHẠM" if clue["criminal"] else "VÔ TỘI"
        return f"{clue['cell']} chắc chắn là {status}."
    if kind == "SAME":
        return " và ".join(clue["cells"]) + " có cùng trạng thái."
    if kind == "DIFFERENT":
        return " và ".join(clue["cells"]) + " có trạng thái khác nhau."
    if kind == "EXACTLY":
        return f"Có đúng {clue['k']} tội phạm trong {region_text(clue['region'])}."
    if kind == "AT_LEAST":
        return f"Có ít nhất {clue['k']} tội phạm trong {region_text(clue['region'])}."
    if kind == "AT_MOST":
        return f"Có nhiều nhất {clue['k']} tội phạm trong {region_text(clue['region'])}."
    return "Loại manh mối chưa hỗ trợ hiển thị."


def short_clue(clue: dict, max_chars: int = 65) -> str:
    content = clue_text(clue)
    return content if len(content) <= max_chars else content[: max_chars - 1].rstrip() + "…"
