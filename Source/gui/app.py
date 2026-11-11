"""Tkinter front end. Uses only GameController public methods / PublicState."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from experiments.run_experiments import main
from controller import GameController
from gui import theme as t
from gui.board import BoardCanvas
from gui.formatting import clue_text, short_clue
from regions import referenced_cells


class GriductiveApp:
    def __init__(self, root: tk.Tk, controller: GameController, default_path: Path, on_back=None):
        self.root, self.controller = root, controller
        self.default_path = Path(default_path)
        self.on_back = on_back
        self.selected: str | None = None
        self.selected_clue: str | None = None
        self.highlight: set[str] = set()
        self.auto_running = False
        self.auto_job: str | None = None
        self.state: dict = {}
        self.clue_ids: list[str] = []
        self.root.title("Griductive — Logic Detective")
        self.root.configure(bg=t.BG)
        # Respect available desktop height (e.g. 1366x768 laptops / Windows taskbar).
        # Layout below reserves space for the deduction log even in short windows.
        self.root.state("zoomed")
        self._build()
        self.load(self.default_path)

    def _label(self, parent, text: str, *, size=11, color=t.TEXT, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=(t.FONT, size, "bold" if bold else "normal"), **kwargs)

    def _button(self, parent, text: str, command, *, bg=t.PANEL_2, fg=t.TEXT,
                active=None, pad=14):
        widget = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                           activebackground=active or bg, activeforeground=fg,
                           disabledforeground=t.FAINT, relief="flat", bd=0,
                           highlightthickness=0, cursor="hand2", font=(t.FONT, 10, "bold"),
                           padx=pad, pady=6)
        widget.bind("<Enter>", lambda event: widget.config(bg=active or t.CARD_HOVER)
                    if widget.cget("state") == "normal" else None)
        widget.bind("<Leave>", lambda event: widget.config(bg=bg))
        return widget

    def _build(self):
        head = tk.Frame(self.root, bg=t.BG, padx=22, pady=9)
        head.pack(fill="x")
        brand = tk.Frame(head, bg=t.BG)
        brand.pack(side="left")
        self._label(brand, "◈  GRIDUCTIVE", size=20, color=t.TEAL, bold=True).pack(anchor="w")
        self._label(brand, "LOGIC DETECTIVE  /  PROJECT 2", size=10,
                    color=t.MUTED, bold=True).pack(anchor="w", pady=(4, 0))
        actions = tk.Frame(head, bg=t.BG)
        actions.pack(side="right", pady=0)
        if self.on_back is not None:
            self._button(
                actions,
                "←  CHỌN MÀN",
                self.on_back,
                pad=10
            ).pack(
                side="left",
                padx=(0, 8)
            )
        for title, callback, bg, active in (
            ("↥  LOAD", self._pick_puzzle, t.PANEL_2, t.CARD_HOVER),
            ("↻  RESTART", self.restart, t.PANEL_2, t.CARD_HOVER),
            ("✧  HINT", self.hint, t.TEAL_DARK, t.CARD_HOVER),
        ):
            self._button(actions, title, callback, bg=bg, active=active).pack(side="left", padx=5)
        self.auto_button = self._button(actions, "▶  AUTO SOLVE", self.toggle_auto,
                                        bg=t.TEAL, fg=t.BG, active="#6BE8DB", pad=20)
        self.auto_button.pack(side="left", padx=(6, 0))
        line = tk.Frame(self.root, bg=t.LINE, height=1)
        line.pack(fill="x", padx=30)
        main = tk.Frame(self.root, bg=t.BG)
        main.pack(fill="both", expand=True, padx=16, pady=(7, 9))
        main.grid_columnconfigure(0, weight=8, uniform="panes")
        main.grid_columnconfigure(1, weight=4, uniform="panes")
        main.grid_rowconfigure(0, weight=1)
        left = tk.Frame(main, bg=t.PANEL, padx=12, pady=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(4, 10))
        panel_head = tk.Frame(left, bg=t.PANEL)
        panel_head.pack(fill="x", pady=(0, 4))
        self.level_label = self._label(panel_head, "CASE FILE", size=13, bold=True)
        self.level_label.pack(side="left")
        self.progress_label = self._label(panel_head, "0 / 0", size=11,
                                          color=t.TEAL, bold=True)
        self.progress_label.pack(side="right")
        
        self.board = BoardCanvas(left, self.select_cell)
        self.board.pack(fill="both", expand=True)

        foot = tk.Frame(left, bg=t.PANEL, pady=4)
        foot.pack(fill="x")
        self._label(foot, "● VÔ TỘI", size=9, color=t.TEAL, bold=True).pack(side="left", padx=(4, 15))
        self._label(foot, "● TỘI PHẠM", size=9, color=t.RED, bold=True).pack(side="left")
        self._label(foot, "◇ Vùng manh mối", size=9, color=t.GOLD).pack(side="right", padx=6)

        right = tk.Frame(main, bg=t.PANEL, padx=23, pady=20)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 4))
        self._label(right, "HỒ SƠ ĐIỀU TRA", size=12, color=t.MUTED, bold=True).pack(anchor="w")
        self.person_title = self._label(right, "Chọn một nhân vật", size=19, bold=True)
        self.person_title.pack(anchor="w", pady=(10, 3))
        self.person_meta = self._label(right, "", size=10, color=t.MUTED)
        self.person_meta.pack(anchor="w")
        self.person_status = self._label(right, "", size=10, color=t.GOLD, bold=True)
        self.person_status.pack(anchor="w", pady=(9, 9))
        self.clue_detail = self._label(right, "", size=11, color=t.TEXT,
                                        justify="left", anchor="nw", wraplength=330)
        self.clue_detail.pack(fill="x", pady=(0, 12))
        buttons = tk.Frame(right, bg=t.PANEL)
        buttons.pack(fill="x", pady=(0, 17))
        self.criminal_button = self._button(buttons, "TỘI PHẠM", lambda: self.verdict("CRIMINAL"),
                                            bg=t.RED_DARK, fg=t.RED, active="#66384E")
        self.criminal_button.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.innocent_button = self._button(buttons, "VÔ TỘI", lambda: self.verdict("INNOCENT"),
                                            bg=t.TEAL_DARK, fg=t.TEAL, active="#1C595E")
        self.innocent_button.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Frame(right, bg=t.LINE, height=1).pack(fill="x", pady=(0, 15))
        clue_bar = tk.Frame(right, bg=t.PANEL)
        clue_bar.pack(fill="x")
        self._label(clue_bar, "MANH MỐI ĐÃ MỞ", size=11, bold=True).pack(side="left")
        self.clue_count = self._label(clue_bar, "0", size=10, color=t.MUTED)
        self.clue_count.pack(side="right")
        # Reserve the bottom section BEFORE packing the expandable clue list.
        # Otherwise the list can consume all vertical space and clip the log.
        log_panel = tk.Frame(right, bg=t.PANEL)
        log_panel.pack(side="bottom", fill="x")
        self.log_title = self._label(log_panel, "NHẬT KÝ SUY LUẬN", size=11, bold=True)
        self.log_title.pack(anchor="w", pady=(0, 7))
        self.log = tk.Text(log_panel, height=4, bg=t.PANEL_2, fg=t.MUTED,
                           insertbackground=t.TEAL, font=(t.FONT, 10), wrap="word",
                           relief="flat", borderwidth=0, padx=10, pady=8,
                           state="disabled")
        self.log.pack(fill="x")

        # The clue list takes ONLY the remaining space and can scroll when short.
        clue_area = tk.Frame(right, bg=t.PANEL)
        clue_area.pack(fill="both", expand=True, pady=(9, 12))
        self.clue_list = tk.Listbox(clue_area, height=5, font=(t.FONT, 10), bg=t.PANEL_2,
                                    fg=t.TEXT, selectbackground=t.TEAL_DARK,
                                    selectforeground=t.TEAL, activestyle="none",
                                    relief="flat", bd=0, highlightthickness=0,
                                    exportselection=False)
        self.clue_list.pack(fill="both", expand=True, side="left")
        scroll = tk.Scrollbar(clue_area, command=self.clue_list.yview)
        scroll.pack(side="right", fill="y")
        self.clue_list.configure(yscrollcommand=scroll.set)
        self.clue_list.bind("<<ListboxSelect>>", self._select_clue)
        footer = tk.Frame(self.root, bg=t.BG, padx=30, pady=8)
        footer.pack(fill="x")
        self.status_text = self._label(footer, "", size=10, color=t.MUTED, anchor="w")
        self.status_text.pack(side="left", fill="x", expand=True)
        self._label(footer,"LOGIC AGENT  ·  CNF / DPLL",size=9,color=t.TEAL,bold=True).pack(side="right")
        self.root.bind("<Escape>", lambda event: self.stop_auto())

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", "• " + text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _status(self, text: str, color=t.MUTED):
        self.status_text.configure(text=text, fg=color)

    def _pick_puzzle(self):
        path = filedialog.askopenfilename(title="Load Griductive JSON", initialdir=str(self.default_path.parent),
                                           filetypes=[("Puzzle JSON", "*.json")])
        if path:
            self.load(Path(path))

    def _cancel_job(self):
        self.auto_running = False
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        self.auto_button.configure(text="▶  AUTO SOLVE")

    def stop_auto(self):
        self._cancel_job()
        self._status("Đã dừng tự động giải.")

    def load(self, path: Path):
        self._cancel_job()
        try:
            self.state = self.controller.load(path)
        except (ValueError, OSError, RuntimeError) as error:
            messagebox.showerror("Không thể tải màn", str(error))
            return
        self.selected = None
        self.selected_clue = None
        self.highlight = set()
        self.level_label.config(text=f"CASE FILE  /  {self.state['puzzle_id']}")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self._log("Đã tải màn. Chỉ thẻ mở mới cung cấp manh mối.")
        self._status("Chọn nhân vật, đọc manh mối và đưa ra kết luận có thể chứng minh.")
        self.refresh()

    def restart(self):
        self._cancel_job()
        self.state = self.controller.restart()
        self.selected, self.selected_clue = None, None
        self.highlight.clear()
        self._log("Bắt đầu lại màn chơi.")
        self._status("Đã đặt lại trạng thái ban đầu.")
        self.refresh()

    def select_cell(self, cell: str):
        self.selected = cell
        owner_clue = next((clue for clue in self.state["revealed_clues"]
                           if clue["owner"] == cell), None)
        self.selected_clue = owner_clue["id"] if owner_clue else None
        if owner_clue is None:
            self.highlight.clear()
        self.refresh()

    def _select_clue(self, event):
        selection = self.clue_list.curselection()
        if not selection or selection[0] >= len(self.clue_ids):
            return
        self.selected_clue = self.clue_ids[selection[0]]
        clue = next((c for c in self.state["revealed_clues"] if c["id"] == self.selected_clue), None)
        if clue is not None:
            self.highlight = set(referenced_cells(clue, self.state["size"]))
            self._status(f"Đang làm sáng các ô được nhắc đến bởi {clue['id']}.", t.GOLD)
            self.board.render(self.state, self.selected, self.highlight)
            self.clue_detail.config(text=clue_text(clue))

    def refresh(self):
        self.state = self.controller.engine.get_public_state()
        n = self.state["size"]
        count = len(self.state["known_statuses"])
        self.progress_label.config(text=f"{count} / {n*n} MỞ")
        if self.selected_clue:
            clue = next((c for c in self.state["revealed_clues"] if c["id"] == self.selected_clue), None)
            self.highlight = set(referenced_cells(clue, n)) if clue else set()
        self.board.render(self.state, self.selected, self.highlight)
        person = next((c for c in self.state["characters"] if c["cell"] == self.selected), None)
        if person is None:
            self.person_title.config(text="Chọn một nhân vật")
            self.person_meta.config(text="Nhấp vào thẻ để mở hồ sơ.")
            self.person_status.config(text="CHƯA CÓ LỰA CHỌN")
            self.clue_detail.config(text="Chỉ kết luận được chứng minh mới lật được thẻ.")
        else:
            self.person_title.config(text=person["name"])
            self.person_meta.config(text=f"{person['cell']}  ·  {person['profession']}")
            if self.selected in self.state["known_statuses"]:
                criminal = self.state["known_statuses"][self.selected]
                self.person_status.config(text="● TỘI PHẠM" if criminal else "● VÔ TỘI",
                                          fg=t.RED if criminal else t.TEAL)
                clue = next(c for c in self.state["revealed_clues"] if c["owner"] == self.selected)
                self.clue_detail.config(text=clue_text(clue))
            else:
                self.person_status.config(text="◇ CHƯA XÁC ĐỊNH", fg=t.GOLD)
                self.clue_detail.config(text="Manh mối trên thẻ này đang bị ẩn. Hãy dựa vào manh mối đã công khai.")
        self.criminal_button.configure(state="normal" if person and self.selected not in self.state["known_statuses"] else "disabled")
        self.innocent_button.configure(state="normal" if person and self.selected not in self.state["known_statuses"] else "disabled")
        self.clue_ids = [c["id"] for c in self.state["revealed_clues"]]
        self.clue_count.configure(text=f"{len(self.clue_ids)} CLUES")
        self.clue_list.delete(0, "end")
        for clue in self.state["revealed_clues"]:
            self.clue_list.insert("end", f" {clue['owner']}   {short_clue(clue, 55)}")
        if self.selected_clue in self.clue_ids:
            index = self.clue_ids.index(self.selected_clue)
            self.clue_list.selection_clear(0, "end")
            self.clue_list.selection_set(index)
            self.clue_list.see(index)
        if count == n*n:
            self._status("HOÀN THÀNH — tất cả kết luận đã được chứng minh!", t.TEAL)

    def verdict(self, verdict: str):
        if not self.selected or self.auto_running:
            return
        self._submit(self.selected, verdict)

    def _submit(self, cell: str, verdict: str):
        try:
            result = self.controller.submit(cell, verdict)
        except (NotImplementedError, ValueError) as error:
            self._status(str(error), t.RED)
            self._log(str(error))
            return None
        messages = {
            "ACCEPTED": "CHẤP NHẬN — thẻ đã lật, thêm manh mối mới",
            "NOT_PROVABLE": "KHÔNG THỂ CHỨNG MINH — không mở thẻ",
            "CONTRADICTED": "BỊ PHẢN BÁC — kết luận ngược lại mới đúng",
            "PUZZLE_ERROR": "LỖI DỮ LIỆU MÀN — trạng thái giữ nguyên",
            "INCONSISTENT": "TRI THỨC MÂU THUẪN — trạng thái giữ nguyên",
        }
        note = messages.get(result.status, result.status)
        self._log(f"{cell} → {verdict} : {note}")
        self._status(note, t.TEAL if result.status == "ACCEPTED" else t.RED)
        self.state = result.public_state
        self.selected = cell
        if result.status == "ACCEPTED" and result.revealed_clue:
            self.selected_clue = result.revealed_clue["id"]
        self.refresh()
        return result

    def hint(self):
        if self.auto_running:
            return
        try:
            move = self.controller.hint()
        except (NotImplementedError, ValueError) as error:
            self._status(str(error), t.RED)
            return
        if move.status == "MOVE":
            self.selected = move.cell
            self.selected_clue = move.relevant_clue_ids[0] if move.relevant_clue_ids else None
            self.refresh()
            text = f"GỢI Ý: {move.cell} có thể được chứng minh là {move.verdict}."
            self._status(text, t.TEAL)
            self._log(text)
        else:
            message = {"STUCK": "Logic Agent chưa tìm thấy bước có thể chứng minh.",
                       "SOLVED": "Màn đã hoàn tất.",
                       "INCONSISTENT": "Tri thức công khai mâu thuẫn."}.get(move.status, move.status)
            self._status(message, t.GOLD)
            self._log(message)

    def toggle_auto(self):
        if self.auto_running:
            self.stop_auto()
        else:
            self.auto_running = True
            self.auto_button.config(text="■  STOP")
            self.auto_job = self.root.after(40, self._next_auto)

    def _next_auto(self):
        self.auto_job = None
        if not self.auto_running:
            return
        try:
            move = self.controller.hint()
        except (NotImplementedError, ValueError) as error:
            self._cancel_job()
            self._status(str(error), t.RED)
            return
        if move.status != "MOVE":
            self._cancel_job()
            text = {"SOLVED": "Tất cả thẻ đã được giải.",
                    "STUCK": "Logic Agent chưa tìm thấy bước có thể chứng minh.",
                    "INCONSISTENT": "KB mâu thuẫn."}.get(move.status, move.status)
            self._log("AUTO: " + text)
            self._status("AUTO: " + text, t.TEAL if move.status == "SOLVED" else t.GOLD)
            return
        self.selected = move.cell
        result = self._submit(move.cell, move.verdict)
        if result is None or result.status != "ACCEPTED":
            self._cancel_job()
            return
        if self.auto_running:
            self.auto_job = self.root.after(380, self._next_auto)
