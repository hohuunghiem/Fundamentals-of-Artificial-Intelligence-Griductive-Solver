"""Title screen, level selection and game rules."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from gui import theme as t
from gui.app import GriductiveApp



SOURCE = Path(__file__).resolve().parents[1]


LEVELS = [
    ("3×3 EASY", "demo_3x3.json", "Làm quen với manh mối"),
    ("3×3 MEDIUM 1", "level_3x3_medium_01.json", "Suy luận kết hợp"),
    ("3×3 MEDIUM 2", "level_3x3_medium_02.json", "Thử thách vùng đếm"),

    ("4×4 EASY", "demo_4x4.json", "Bàn chơi 16 nhân vật"),
    ("4×4 MEDIUM", "level_4x4_medium.json", "Kết hợp nhiều manh mối"),
    ("4×4 HARD", "level_4x4_hard.json", "Thử thách suy luận nâng cao"),

    ("5×5 MEDIUM 1", "level_5x5_medium.json", "Điều tra bàn 25 nhân vật"),
    ("5×5 MEDIUM 2", "level_5x5_medium_02.json", "Suy luận nhiều bước"),
    ("5×5 HARD", "level_5x5_hard.json", "Thử thách khó nhất"),
]

class GameNavigator:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.game: GriductiveApp | None = None

        root.title("Griductive — Logic Detective")
        root.configure(bg=t.BG)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        width = min(1460, max(800, screen_w - 60))
        height = min(900, max(580, screen_h - 90))

        root.geometry(f"{width}x{height}")
        root.minsize(
            min(940, width),
            min(620, height)
        )

        self.show_home()

    def _clear(self):
        # Hủy Auto Solve trước khi rời màn chơi.
        if self.game is not None:
            self.game.stop_auto()
            self.game = None

        self.root.unbind("<Escape>")

        for widget in self.root.winfo_children():
            widget.destroy()

    def _page(self):
        self._clear()

        page = tk.Frame(self.root, bg=t.BG)
        page.pack(fill="both", expand=True)

        return page

    def _button(
        self,
        parent,
        title,
        command,
        primary=False,
        enabled=True
    ):
        return tk.Button(
            parent,
            text=title,
            command=command,
            font=(t.FONT, 12, "bold"),
            bg=t.TEAL if primary and enabled else t.PANEL_2,
            fg=(
                t.BG if primary and enabled
                else t.TEXT if enabled
                else t.FAINT
            ),
            activebackground=(
                "#65E5D7" if primary else t.CARD_HOVER
            ),
            activeforeground=(
                t.BG if primary else t.TEXT
            ),
            disabledforeground=t.FAINT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=22,
            pady=11,
            cursor="hand2" if enabled else "arrow",
            state="normal" if enabled else "disabled",
        )
    def show_home(self):
        page = self._page()

        center = tk.Frame(page, bg=t.BG)
        center.place(
            relx=0.5,
            rely=0.48,
            anchor="center"
        )

        # Logo: bàn cờ và kính lúp
        logo = tk.Canvas(
            center,
            width=132,
            height=118,
            bg=t.BG,
            highlightthickness=0
        )
        logo.pack(pady=(0, 5))

        # Vẽ lưới 3x3
        for row in range(3):
            for col in range(3):
                x = 28 + col * 23
                y = 17 + row * 23

                logo.create_rectangle(
                    x, y,
                    x + 16, y + 16,
                    fill=t.PANEL_2,
                    outline=t.TEAL,
                    width=2
                )

        # Vẽ kính lúp
        logo.create_oval(
            62, 47, 99, 84,
            outline=t.GOLD,
            width=5
        )

        logo.create_line(
            94, 78, 117, 101,
            fill=t.GOLD,
            width=6
        )

        # Tên game
        tk.Label(
            center,
            text="GRIDUCTIVE",
            font=(t.FONT, 42, "bold"),
            fg=t.TEAL,
            bg=t.BG
        ).pack()

        tk.Label(
            center,
            text="LOGIC DETECTIVE  •  PROJECT 2",
            font=(t.FONT, 12, "bold"),
            fg=t.MUTED,
            bg=t.BG
        ).pack(pady=(4, 18))

        tk.Label(
            center,
            text=(
                "Khám phá sự thật bằng suy luận logic. "
                "Không phỏng đoán."
            ),
            font=(t.FONT, 13),
            fg=t.TEXT,
            bg=t.BG
        ).pack(pady=(0, 30))

        # Nút chọn màn
        self._button(
            center,
            "▶  CHỌN MÀN CHƠI",
            self.show_levels,
            primary=True
        ).pack(fill="x", pady=6)

        # Nút luật chơi
        self._button(
            center,
            "📖  LUẬT CHƠI",
            self.show_rules
        ).pack(fill="x", pady=6)

        # Footer
        tk.Label(
            page,
            text=(
                "CSC14003  •  "
                "INTRODUCTION TO ARTIFICIAL INTELLIGENCE"
            ),
            font=(t.FONT, 9),
            fg=t.FAINT,
            bg=t.BG
        ).pack(side="bottom", pady=14)
    def show_levels(self):
        page = self._page()

        # Thanh tiêu đề
        header = tk.Frame(
            page,
            bg=t.BG,
            padx=34,
            pady=22
        )
        header.pack(fill="x")

        self._button(
            header,
            "←  TRANG CHỦ",
            self.show_home
        ).pack(side="left")

        tk.Label(
            header,
            text="CHỌN MÀN CHƠI",
            font=(t.FONT, 26, "bold"),
            fg=t.TEXT,
            bg=t.BG
        ).pack(side="left", padx=24)

        tk.Label(
            page,
            text="Chọn vụ án để bắt đầu điều tra",
            font=(t.FONT, 12),
            fg=t.MUTED,
            bg=t.BG
        ).pack(anchor="w", padx=40)

        # Grid chứa danh sách màn
        grid = tk.Frame(page, bg=t.BG)
        grid.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(15, 20)
        )

        # Cả 3 cột có chiều rộng bằng nhau
        for col in range(3):
            grid.grid_columnconfigure(
                col,
                weight=1,
                uniform="level_columns"
            )

        # Cả 3 hàng có chiều cao bằng nhau
        for row in range(3):
            grid.grid_rowconfigure(
                row,
                weight=1,
                uniform="level_rows"
            )

        

        # Tạo các thẻ màn chơi
        for i, (title, filename, description) in enumerate(LEVELS):
            row, col = divmod(i, 3)

            path = SOURCE / "puzzles" / filename
            available = path.is_file()

            card = tk.Frame(
                grid,
                bg=t.PANEL,
                padx=18,
                pady=12,
                highlightbackground=t.LINE,
                highlightthickness=1
            )

            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=7,
                pady=7
            )

            tk.Label(
                card,
                text=title,
                font=(t.FONT, 17, "bold"),
                fg=t.TEAL if available else t.MUTED,
                bg=t.PANEL
            ).pack(anchor="w")

            tk.Label(
                card,
                text=description,
                font=(t.FONT, 10),
                fg=t.MUTED,
                bg=t.PANEL
            ).pack(anchor="w", pady=(4, 8))

            button_text = (
                "▶  BẮT ĐẦU"
                if available
                else "CHƯA CÓ DỮ LIỆU MÀN"
            )

            self._button(
                card,
                button_text,
                lambda p=path: self.open_level(p),
                primary=available,
                enabled=available
            ).pack(anchor="w")
    def show_rules(self):
        page = self._page()

        header = tk.Frame(
            page,
            bg=t.BG,
            padx=34,
            pady=22
        )
        header.pack(fill="x")

        self._button(
            header,
            "←  TRANG CHỦ",
            self.show_home
        ).pack(side="left")

        tk.Label(
            header,
            text="LUẬT CHƠI GRIDUCTIVE",
            font=(t.FONT, 26, "bold"),
            fg=t.TEXT,
            bg=t.BG
        ).pack(side="left", padx=24)

        content = tk.Frame(page, bg=t.BG)
        content.pack(
            fill="both",
            expand=True,
            padx=38,
            pady=(2, 10)
        )

        content.grid_columnconfigure(
            0, weight=1, uniform="rules"
        )
        content.grid_columnconfigure(
            1, weight=1, uniform="rules"
        )

        for row in range(3):
            content.grid_rowconfigure(row, weight=1)

        rules = [
            (
                "1. Mục tiêu",
                "Xác định trạng thái của tất cả nhân vật: "
                "TỘI PHẠM hoặc VÔ TỘI."
            ),
            (
                "2. Thông tin công khai",
                "Một vài thẻ được mở sẵn. Thẻ mở cho biết trạng thái "
                "và manh mối. Mọi manh mối đều đúng, "
                "kể cả trên thẻ tội phạm."
            ),
            (
                "3. Không được đoán",
                "Chỉ kết luận khi trạng thái được chứng minh từ "
                "các manh mối đã mở. Nếu không thể chứng minh, "
                "thẻ không được mở."
            ),
            (
                "4. Các loại manh mối",
                "FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, "
                "AT_MOST. Vùng có thể là hàng, cột, "
                "8 ô lân cận hoặc danh sách ô."
            ),
            (
                "5. Cách chơi",
                "Chọn nhân vật rồi chọn TỘI PHẠM / VÔ TỘI. "
                "Nếu hợp lệ, thẻ lật và hiện manh mối. "
                "Có thể chọn manh mối để tô sáng các ô liên quan."
            ),
            (
                "6. Công cụ hỗ trợ",
                "HINT gợi ý kết luận có thể chứng minh; "
                "AUTO SOLVE tự thực hiện; "
                "RESTART chơi lại màn từ đầu."
            ),
        ]

        for i, (title, body) in enumerate(rules):
            card = tk.Frame(
                content,
                bg=t.PANEL,
                padx=18,
                pady=14,
                highlightbackground=t.LINE,
                highlightthickness=1
            )

            card.grid(
                row=i // 2,
                column=i % 2,
                sticky="nsew",
                padx=7,
                pady=7
            )

            tk.Label(
                card,
                text=title,
                font=(t.FONT, 14, "bold"),
                fg=t.TEAL,
                bg=t.PANEL
            ).pack(anchor="w", pady=(0, 8))

            tk.Label(
                card,
                text=body,
                font=(t.FONT, 11),
                fg=t.TEXT,
                bg=t.PANEL,
                justify="left",
                wraplength=360
            ).pack(anchor="w")

        self._button(
            page,
            "▶  ĐẾN CHỌN MÀN",
            self.show_levels,
            primary=True
        ).pack(pady=(0, 18))
    def open_level(self, path: Path):
        if not path.is_file():
            messagebox.showwarning(
                "Chưa có màn",
                f"Không tìm thấy file: {path.name}"
            )
            return

        self._clear()

        self.game = GriductiveApp(
            self.root,
            self.controller,
            path,
            on_back=self.show_levels
        )