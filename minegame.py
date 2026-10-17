
import tkinter as tk
from tkinter import messagebox
import random
import time


# -------------------- THEME --------------------

BG = "#0B1220"
PANEL = "#111D30"
PANEL_LIGHT = "#1A2A42"
TILE = "#263B57"
TILE_HOVER = "#344D6D"
REVEALED = "#DCE6F2"
ACCENT = "#2389FF"
TEXT = "#EAF2FF"
MUTED = "#91A4C2"

NUMBER_COLORS = {
    1: "#1769E0",
    2: "#159447",
    3: "#E34B4B",
    4: "#743DCE",
    5: "#A63E31",
    6: "#008C95",
    7: "#182235",
    8: "#65758B",
}

DIFFICULTIES = {
    "Beginner": (9, 9, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (16, 30, 99),
}


# -------------------- GAME --------------------

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper | Classic Edition")
        self.root.configure(bg=BG)
        self.root.minsize(650, 600)

        self.rows = 9
        self.cols = 9
        self.mine_count = 10

        self.timer_id = None
        self.start_time = None
        self.elapsed = 0
        self.first_click = True
        self.game_finished = False

        self.cells = []
        self.flags = set()
        self.revealed = set()
        self.mines = set()
        self.buttons = []

        self.build_interface()
        self.new_game()

    # -------------------- INTERFACE --------------------

    def build_interface(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            header,
            text="💣  MINESWEEPER",
            font=("Segoe UI", 24, "bold"),
            bg=BG,
            fg=TEXT,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Find every safe cell. Avoid the mines!",
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w", pady=(3, 0))

        # Status cards
        status = tk.Frame(self.root, bg=PANEL)
        status.pack(fill="x", padx=20, pady=8)

        status.columnconfigure((0, 1, 2), weight=1)

        self.mine_label = tk.Label(
            status,
            text="💣  Mines: 10",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL,
            fg=TEXT,
            pady=14,
        )
        self.mine_label.grid(row=0, column=0, sticky="ew")

        self.face_button = tk.Button(
            status,
            text="🙂",
            command=self.new_game,
            font=("Segoe UI Emoji", 18),
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=TILE_HOVER,
            relief="flat",
            cursor="hand2",
        )
        self.face_button.grid(row=0, column=1, padx=5, pady=6)

        self.timer_label = tk.Label(
            status,
            text="⏱  Time: 000",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL,
            fg=TEXT,
            pady=14,
        )
        self.timer_label.grid(row=0, column=2, sticky="ew")

        # Game controls
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", padx=20, pady=8)

        tk.Label(
            controls,
            text="Difficulty",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(0, 8))

        self.difficulty = tk.StringVar(value="Beginner")

        self.difficulty_menu = tk.OptionMenu(
            controls,
            self.difficulty,
            *DIFFICULTIES.keys(),
            command=self.change_difficulty,
        )
        self.difficulty_menu.config(
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=TILE_HOVER,
            activeforeground=TEXT,
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        self.difficulty_menu["menu"].config(
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="white",
        )
        self.difficulty_menu.pack(side="left")

        tk.Button(
            controls,
            text="↻  Restart",
            command=self.new_game,
            bg=ACCENT,
            fg="white",
            activebackground="#1168D5",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=12,
            pady=6,
        ).pack(side="right")

        # Custom board settings
        custom = tk.Frame(self.root, bg=PANEL)
        custom.pack(fill="x", padx=20, pady=6)

        tk.Label(
            custom,
            text="Custom board",
            font=("Segoe UI", 10, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=10, pady=(8, 4))

        self.row_var = tk.StringVar(value="9")
        self.col_var = tk.StringVar(value="9")
        self.mine_var = tk.StringVar(value="10")

        self.add_setting(custom, "Rows", self.row_var, 0, 1)
        self.add_setting(custom, "Columns", self.col_var, 2, 3)
        self.add_setting(custom, "Mines", self.mine_var, 4, 5)

        custom.columnconfigure((1, 3, 5), weight=1)

        tk.Button(
            custom,
            text="Apply",
            command=self.apply_custom,
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=TILE_HOVER,
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=10,
        ).grid(row=1, column=6, padx=8, pady=8)

        # Board container
        self.board_outer = tk.Frame(
            self.root,
            bg=PANEL,
            padx=10,
            pady=10,
        )
        self.board_outer.pack(
            padx=20,
            pady=10,
            expand=True,
            fill="both",
        )

        self.board_frame = tk.Frame(self.board_outer, bg=PANEL)
        self.board_frame.pack(expand=True)

        tk.Label(
            self.root,
            text="Left-click: reveal     Right-click: flag / unflag",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(pady=(0, 14))

    def add_setting(self, parent, label, variable, label_col, entry_col):
        tk.Label(
            parent,
            text=label,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).grid(row=1, column=label_col, padx=(10, 4), pady=8)

        tk.Entry(
            parent,
            textvariable=variable,
            width=5,
            bg=BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
        ).grid(row=1, column=entry_col, padx=4, pady=8, sticky="ew")

    # -------------------- GAME SETUP --------------------

    def change_difficulty(self, choice):
        rows, cols, mines = DIFFICULTIES[choice]

        self.rows = rows
        self.cols = cols
        self.mine_count = mines

        self.row_var.set(str(rows))
        self.col_var.set(str(cols))
        self.mine_var.set(str(mines))

        self.new_game()

    def apply_custom(self):
        try:
            rows = int(self.row_var.get())
            cols = int(self.col_var.get())
            mines = int(self.mine_var.get())

            if not (2 <= rows <= 24 and 2 <= cols <= 30):
                raise ValueError("Rows must be 2–24 and columns 2–30.")

            if not (1 <= mines < rows * cols):
                raise ValueError(
                    "Mines must be at least 1 and fewer than total cells."
                )

        except ValueError as error:
            messagebox.showerror("Invalid settings", str(error))
            return

        self.rows = rows
        self.cols = cols
        self.mine_count = mines

        self.difficulty.set("Custom")
        self.new_game()

    def new_game(self):
        self.stop_timer()

        self.first_click = True
        self.game_finished = False
        self.start_time = None
        self.elapsed = 0

        self.flags = set()
        self.revealed = set()

        self.mines = set(
            random.sample(
                range(self.rows * self.cols),
                self.mine_count,
            )
        )

        self.mine_label.config(text=f"💣  Mines: {self.mine_count}")
        self.timer_label.config(text="⏱  Time: 000")
        self.face_button.config(text="🙂")

        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.cells = []
        self.buttons = []

        # Smaller cells allow larger boards to fit more easily.
        cell_size = 36 if self.cols <= 12 else (
            28 if self.cols <= 20 else 22
        )

        font_size = 12 if self.cols <= 12 else 9

        for r in range(self.rows):
            row_buttons = []

            for c in range(self.cols):
                index = r * self.cols + c

                button = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    font=("Segoe UI", font_size, "bold"),
                    bg=TILE,
                    fg=TEXT,
                    activebackground=TILE_HOVER,
                    activeforeground=TEXT,
                    relief="raised",
                    bd=2,
                    cursor="hand2",
                    command=lambda i=index: self.reveal_cell(i),
                )

                button.grid(
                    row=r,
                    column=c,
                    padx=1,
                    pady=1,
                    ipadx=max(0, (cell_size - 24) // 2),
                    ipady=max(0, (cell_size - 24) // 2),
                )

                button.bind(
                    "<Button-3>",
                    lambda event, i=index: self.toggle_flag(i),
                )

                # Right-click support for macOS trackpads.
                button.bind(
                    "<Control-Button-1>",
                    lambda event, i=index: self.toggle_flag(i),
                )

                row_buttons.append(button)

            self.buttons.append(row_buttons)

        self.cells = [
            self.neighbor_count(i)
            for i in range(self.rows * self.cols)
        ]

    # -------------------- MINES & NEIGHBORS --------------------

    def get_neighbors(self, index):
        row, col = divmod(index, self.cols)
        neighbors = []

        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                other = r * self.cols + c

                if other != index:
                    neighbors.append(other)

        return neighbors

    def neighbor_count(self, index):
        return sum(
            neighbor in self.mines
            for neighbor in self.get_neighbors(index)
        )

    def get_button(self, index):
        row, col = divmod(index, self.cols)
        return self.buttons[row][col]

    # -------------------- REVEAL CELLS --------------------

    def reveal_cell(self, index):
        if self.game_finished or index in self.revealed:
            return

        if index in self.flags:
            return

        # Guarantee that the first click never hits a mine.
        if self.first_click:
            self.first_click = False

            if index in self.mines:
                self.mines.remove(index)

                available = [
                    i for i in range(self.rows * self.cols)
                    if i != index and i not in self.mines
                ]
                self.mines.add(random.choice(available))

            self.start_timer()

        if index in self.mines:
            self.revealed.add(index)
            self.get_button(index).config(
                text="💣",
                bg="#F04452",
                fg="white",
                relief="sunken",
                disabledforeground="white",
                state="disabled",
            )
            self.end_game(False)
            return

        self.reveal_safe_area(index)
        self.check_win()

    def reveal_safe_area(self, start_index):
        # Iterative flood fill avoids deep recursion.
        stack = [start_index]

        while stack:
            index = stack.pop()

            if index in self.revealed or index in self.flags:
                continue

            if index in self.mines:
                continue

            self.revealed.add(index)

            count = self.neighbor_count(index)
            button = self.get_button(index)

            button.config(
                text=str(count) if count else "",
                bg=REVEALED,
                fg=NUMBER_COLORS.get(count, TEXT),
                activebackground=REVEALED,
                relief="sunken",
                bd=1,
                state="disabled",
                disabledforeground=NUMBER_COLORS.get(count, TEXT),
                cursor="arrow",
            )

            if count == 0:
                for neighbor in self.get_neighbors(index):
                    if (
                        neighbor not in self.revealed
                        and neighbor not in self.flags
                        and neighbor not in self.mines
                    ):
                        stack.append(neighbor)

    # -------------------- FLAGS --------------------

    def toggle_flag(self, index):
        if self.game_finished or index in self.revealed:
            return

        if index in self.flags:
            self.flags.remove(index)

            self.get_button(index).config(
                text="",
                fg=TEXT,
                bg=TILE,
                relief="raised",
            )

        else:
            if len(self.flags) >= self.mine_count:
                return

            self.flags.add(index)

            self.get_button(index).config(
                text="🚩",
                fg="#FF5B67",
                bg="#34455D",
                relief="raised",
            )

        remaining = self.mine_count - len(self.flags)
        self.mine_label.config(text=f"🚩  Mines: {remaining}")

        self.check_win()

    # -------------------- TIMER --------------------

    def start_timer(self):
        if self.timer_id is not None:
            return

        self.start_time = time.monotonic()
        self.update_timer()

    def update_timer(self):
        if self.game_finished or self.start_time is None:
            self.timer_id = None
            return

        self.elapsed = int(time.monotonic() - self.start_time)

        self.timer_label.config(
            text=f"⏱  Time: {self.elapsed:03d}"
        )

        self.timer_id = self.root.after(500, self.update_timer)

    def stop_timer(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    # -------------------- WIN / LOSS --------------------

    def check_win(self):
        safe_cells = self.rows * self.cols - self.mine_count

        if len(self.revealed) == safe_cells:
            self.end_game(True)

    def end_game(self, won):
        if self.game_finished:
            return

        self.game_finished = True
        self.stop_timer()

        self.face_button.config(text="😎" if won else "😵")

        for index in range(self.rows * self.cols):
            button = self.get_button(index)

            if index in self.mines:
                if index not in self.flags:
                    button.config(
                        text="💣",
                        bg="#1F8B59" if won else "#F04452",
                        disabledforeground="white",
                    )
                elif not won:
                    button.config(bg="#1F8B59")

            elif index in self.flags:
                # Incorrectly flagged cell.
                button.config(
                    text="✕",
                    bg="#F59E0B",
                    disabledforeground="#182235",
                )

            button.config(state="disabled")

        if won:
            messagebox.showinfo(
                "Victory!",
                f"🎉 You cleared the board!\nTime: {self.elapsed} seconds",
            )
        else:
            messagebox.showinfo(
                "Game Over",
                "💥 You hit a mine!\nBetter luck next time.",
            )


# -------------------- RUN APP --------------------

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
