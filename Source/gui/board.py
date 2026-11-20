"""A responsive canvas board. Reads *only* PublicState. No secret fields."""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable

from gui import theme as t
from regions import all_cells

from gui.formatting import short_clue

def rounded_rect(canvas: tk.Canvas, x0: float, y0: float, x1: float, y1: float,
                 radius: float, *, fill: str, outline: str = "", width: int = 1,
                 tags: tuple[str, ...] = ()) -> int:
    r = max(0, min(radius, (x1-x0)/2, (y1-y0)/2))
    points = [
        x0+r,y0, x1-r,y0, x1,y0, x1,y0+r,
        x1,y1-r, x1,y1, x1-r,y1, x0+r,y1,
        x0,y1, x0,y1-r, x0,y0+r, x0,y0,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=15, fill=fill,
                                 outline=outline, width=width, tags=tags)


class BoardCanvas(tk.Canvas):
    def __init__(self, master: tk.Misc, on_select: Callable[[str], None]):
        super().__init__(master, bg=t.PANEL, highlightthickness=0, borderwidth=0)
        self._on_select = on_select
        self._state: dict | None = None
        self._selected: str | None = None
        self._highlights: set[str] = set()
        self.bind("<Configure>", lambda event: self.redraw())

    def render(self, state: dict, selected: str | None, highlighted: set[str]) -> None:
        self._state = state
        self._selected = selected
        self._highlights = set(highlighted)
        self.redraw()

    
    
    def redraw(self) -> None:
        self.delete("all")

        state = self._state
        if not state:
            return

        n = state["size"]
        width = self.winfo_width()
        height = self.winfo_height()

        # Chờ Canvas có kích thước thực
        if width < 80 or height < 80:
            return

        # Giảm khoảng trống quanh bàn cờ
        pad_l, pad_r = 28, 9
        pad_top, pad_bottom = 27, 9

        spacing = 8 if n <= 4 else 5

        # Tính card dựa trên không gian thực tế
        available_w = width - pad_l - pad_r
        available_h = height - pad_top - pad_bottom

        card_w = (
            available_w - (n - 1) * spacing
        ) / n

        card_h = (
            available_h - (n - 1) * spacing
        ) / n

        max_card = {3: 176, 4: 145, 5: 120}.get(n, 120)

        card = max(1, min(card_w, card_h, max_card))

        board_size = n * card + (n - 1) * spacing

        x_start = pad_l + max(
            0, (available_w - board_size) / 2
        )
        y_start = pad_top + max(
            0, (available_h - board_size) / 2
        )

        # Font tự thay đổi theo kích thước card
        name_size = max(8, min(13, round(card * 0.11)))
        meta_size = max(7, min(10, round(card * 0.09)))
        status_size = max(7, min(9, round(card * 0.075)))
        id_size = max(7, min(9, round(card * 0.08)))

        name_font = tkfont.Font(
            family=t.FONT, size=name_size, weight="bold"
        )
        meta_font = tkfont.Font(
            family=t.FONT, size=meta_size
        )
        status_font = tkfont.Font(
            family=t.FONT, size=status_size, weight="bold"
        )
        id_font = tkfont.Font(
            family=t.FONT, size=id_size
        )

        # Rút gọn văn bản thành đúng một dòng
        def fit_text(value, font, max_width):
            value = str(value)

            if font.measure(value) <= max_width:
                return value

            while value and font.measure(value + "…") > max_width:
                value = value[:-1]

            return value.rstrip() + "…"

        # Nhãn cột
        for col in range(n):
            x = x_start + col * (card + spacing) + card / 2
            self.create_text(
                x, y_start - 17,
                text=chr(65 + col),
                fill=t.MUTED,
                font=(t.FONT, 10, "bold")
            )

        # Nhãn hàng
        for row in range(n):
            y = y_start + row * (card + spacing) + card / 2
            self.create_text(
                x_start - 16, y,
                text=str(row + 1),
                fill=t.MUTED,
                font=(t.FONT, 10, "bold")
            )

        people = {
            c["cell"]: c for c in state["characters"]
        }
        statuses = state["known_statuses"]
        clues = {
            c["owner"]: c for c in state["revealed_clues"]
        }

        for idx, cell in enumerate(all_cells(n)):
            row, col = divmod(idx, n)

            x0 = x_start + col * (card + spacing)
            y0 = y_start + row * (card + spacing)
            x1, y1 = x0 + card, y0 + card
            cx = (x0 + x1) / 2

            tag = f"card_{cell}"
            shown = cell in statuses
            chosen = cell == self._selected
            hot = cell in self._highlights

            color = (
                t.RED_DARK if statuses[cell] else t.TEAL_DARK
            ) if shown else t.CARD

            border = (
                t.TEAL if chosen else
                t.GOLD if hot else t.LINE
            )

            rounded_rect(
                self, x0, y0, x1, y1,
                min(12, card * 0.12),
                fill=color,
                outline=border,
                width=3 if chosen or hot else 1,
                tags=(tag,)
            )

            # Mã ô: góc trên trái
            self.create_text(
                x0 + 6, y0 + 5,
                text=cell,
                anchor="nw",
                fill=t.FAINT,
                font=id_font,
                tags=(tag,)
            )

            max_text = max(12, card - 12)

            if shown:
                verdict = (
                    "TỘI PHẠM" if statuses[cell]
                    else "VÔ TỘI"
                )
                accent = t.RED if statuses[cell] else t.TEAL

                # Trạng thái ở dòng riêng
                self.create_text(
                    cx, y0 + max(18, card * 0.23),
                    text=fit_text(
                        verdict, status_font, max_text
                    ),
                    anchor="n",
                    fill=accent,
                    font=status_font,
                    tags=(tag,)
                )

                # Bàn 3x3 có thể hiển thị thêm manh mối
                if n == 3 and card >= 130:
                    name_y = y0 + card * 0.42
                    profession_y = y0 + card * 0.57
                else:
                    name_y = y0 + card * 0.50
                    profession_y = y0 + card * 0.74

                if card < 66:
                    name_y = y0 + card * 0.62

                self.create_text(
                    cx, name_y,
                    text=fit_text(
                        people[cell]["name"],
                        name_font, max_text
                    ),
                    anchor="n",
                    fill=t.TEXT,
                    font=name_font,
                    tags=(tag,)
                )

                if card >= 66:
                    self.create_text(
                        cx, profession_y,
                        text=fit_text(
                            people[cell]["profession"],
                            meta_font, max_text
                        ),
                        anchor="n",
                        fill=t.MUTED,
                        font=meta_font,
                        tags=(tag,)
                    )

                # Manh mối rút gọn chỉ trên bàn 3x3 đủ rộng
                if n == 3 and card >= 130:
                    self.create_line(
                        x0 + 10, y0 + card * 0.69,
                        x1 - 10, y0 + card * 0.69,
                        fill=t.LINE,
                        tags=(tag,)
                    )

                    if cell in clues:
                        self.create_text(
                            cx, y0 + card * 0.79,
                            text=fit_text(
                                short_clue(clues[cell], 35),
                                meta_font, max_text
                            ),
                            anchor="n",
                            fill=t.TEXT,
                            font=meta_font,
                            tags=(tag,)
                        )

            else:
                # Thẻ chưa mở
                orb_y = y0 + card * 0.36
                radius = max(9, min(23, card * 0.16))

                self.create_oval(
                    cx - radius, orb_y - radius,
                    cx + radius, orb_y + radius,
                    fill=t.PANEL_2,
                    outline="",
                    tags=(tag,)
                )

                self.create_text(
                    cx, orb_y,
                    text="?",
                    fill=t.GOLD,
                    font=(
                        t.FONT,
                        max(10, round(card * 0.17)),
                        "bold"
                    ),
                    tags=(tag,)
                )

                self.create_text(
                    cx, y0 + card * 0.64,
                    text=fit_text(
                        people[cell]["name"],
                        name_font, max_text
                    ),
                    anchor="n",
                    fill=t.TEXT,
                    font=name_font,
                    tags=(tag,)
                )

                if card >= 66:
                    self.create_text(
                        cx, y0 + card * 0.81,
                        text=fit_text(
                            people[cell]["profession"],
                            meta_font, max_text
                        ),
                        anchor="n",
                        fill=t.MUTED,
                        font=meta_font,
                        tags=(tag,)
                    )

            # Giữ khả năng click vào thẻ
            self.tag_bind(
                tag, "<Button-1>",
                lambda event, key=cell: self._on_select(key)
            )


