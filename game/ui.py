from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from .board import Board, Direction, MoveResult
from .constants import (
    ANIMATION_DELAY_MS,
    ANIMATION_STEPS,
    BOARD_PIXELS,
    BUTTON_ACTIVE_BG,
    BUTTON_BG,
    CELL_GAP,
    CELL_SIZE,
    DARK_TEXT,
    GRID_BG,
    LIGHT_TEXT,
    TILE_COLORS,
    TILE_FONT_SIZES,
    TILE_TEXT_COLORS,
    WINDOW_BG,
)
from .database import Player, ScoreDatabase
from .storage import persistent_database_path


ENTRY_BG = "#ffffff"
ENTRY_BORDER = "#b9aea4"
TREE_ALT_BG = "#f1ece4"
SELECTION_BG = "#8f7a66"


def configure_ttk_styles(root: tk.Misc) -> None:
    """Use explicit colors so macOS light/dark appearance cannot reduce contrast."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        "Game.TButton",
        background=BUTTON_BG,
        foreground=LIGHT_TEXT,
        bordercolor=BUTTON_BG,
        darkcolor=BUTTON_BG,
        lightcolor=BUTTON_BG,
        focuscolor=BUTTON_BG,
        font=("Arial", 10, "bold"),
        padding=(13, 8),
        relief="flat",
    )
    style.map(
        "Game.TButton",
        background=[
            ("pressed", BUTTON_ACTIVE_BG),
            ("active", BUTTON_ACTIVE_BG),
        ],
        foreground=[
            ("disabled", "#e0d8cf"),
            ("pressed", LIGHT_TEXT),
            ("active", LIGHT_TEXT),
        ],
    )

    style.configure(
        "Primary.Game.TButton",
        background=BUTTON_BG,
        foreground=LIGHT_TEXT,
        bordercolor=BUTTON_BG,
        font=("Arial", 12, "bold"),
        padding=(24, 10),
        relief="flat",
    )
    style.map(
        "Primary.Game.TButton",
        background=[
            ("pressed", BUTTON_ACTIVE_BG),
            ("active", BUTTON_ACTIVE_BG),
        ],
        foreground=[("pressed", LIGHT_TEXT), ("active", LIGHT_TEXT)],
    )

    style.configure(
        "Game.TEntry",
        fieldbackground=ENTRY_BG,
        foreground=DARK_TEXT,
        insertcolor=DARK_TEXT,
        bordercolor=ENTRY_BORDER,
        lightcolor=ENTRY_BORDER,
        darkcolor=ENTRY_BORDER,
        padding=7,
    )
    style.map(
        "Game.TEntry",
        bordercolor=[("focus", BUTTON_BG)],
        lightcolor=[("focus", BUTTON_BG)],
        darkcolor=[("focus", BUTTON_BG)],
        foreground=[("disabled", DARK_TEXT)],
    )

    style.configure(
        "Leaderboard.Treeview",
        background=WINDOW_BG,
        fieldbackground=WINDOW_BG,
        foreground=DARK_TEXT,
        rowheight=29,
        borderwidth=1,
        relief="solid",
        font=("Arial", 11),
    )
    style.map(
        "Leaderboard.Treeview",
        background=[("selected", SELECTION_BG)],
        foreground=[("selected", LIGHT_TEXT)],
    )
    style.configure(
        "Leaderboard.Treeview.Heading",
        background=BUTTON_BG,
        foreground=LIGHT_TEXT,
        bordercolor=GRID_BG,
        font=("Arial", 10, "bold"),
        padding=(6, 8),
        relief="flat",
    )
    style.map(
        "Leaderboard.Treeview.Heading",
        background=[("active", BUTTON_ACTIVE_BG)],
        foreground=[("active", LIGHT_TEXT)],
    )


class PlayerDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, database: ScoreDatabase) -> None:
        super().__init__(parent)
        self.database = database
        self.player: Player | None = None

        self.title("Player Information")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        wrapper = tk.Frame(self, bg=WINDOW_BG, padx=26, pady=24)
        wrapper.pack(fill="both", expand=True)

        tk.Label(
            wrapper,
            text="2048",
            font=("Arial", 42, "bold"),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 4))

        tk.Label(
            wrapper,
            text="Enter your details to start",
            font=("Arial", 13),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.class_name = tk.StringVar()

        fields = (
            ("First name", self.first_name),
            ("Last name", self.last_name),
            ("Class", self.class_name),
        )
        for row, (label, variable) in enumerate(fields, start=2):
            tk.Label(
                wrapper,
                text=label,
                font=("Arial", 11, "bold"),
                fg=DARK_TEXT,
                bg=WINDOW_BG,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=7)

            entry = ttk.Entry(
                wrapper,
                textvariable=variable,
                font=("Arial", 12),
                width=25,
                style="Game.TEntry",
            )
            entry.grid(row=row, column=1, pady=7, ipady=2)
            if row == 2:
                entry.focus_set()

        ttk.Button(
            wrapper,
            text="START GAME",
            command=self.submit,
            style="Primary.Game.TButton",
            cursor="hand2",
        ).grid(row=5, column=0, columnspan=2, pady=(20, 0))

        self.bind("<Return>", lambda _event: self.submit())
        self.update_idletasks()
        self._center(parent)
        self.lift()
        self.focus_force()
        self.after(100, self._activate_modal)

    def _activate_modal(self) -> None:
        if self.winfo_exists():
            self.grab_set()
            self.lift()
            self.focus_force()

    def cancel(self) -> None:
        self.player = None
        self.destroy()

    def _center(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + max(
            0, (parent.winfo_width() - self.winfo_width()) // 2
        )
        y = parent.winfo_rooty() + max(
            0, (parent.winfo_height() - self.winfo_height()) // 2
        )
        self.geometry(f"+{x}+{y}")

    def submit(self) -> None:
        try:
            self.player = self.database.get_or_create_player(
                self.first_name.get(),
                self.last_name.get(),
                self.class_name.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Invalid information", str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                "Database error",
                f"Unable to open the player profile.\n\n{exc}",
                parent=self,
            )
            return
        self.destroy()


class LeaderboardDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, database: ScoreDatabase) -> None:
        super().__init__(parent)
        self.title("Leaderboard")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)
        self.transient(parent)

        tk.Label(
            self,
            text="LEADERBOARD",
            font=("Arial", 24, "bold"),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).pack(pady=(20, 10))

        columns = ("rank", "name", "class", "score")
        tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=10,
            style="Leaderboard.Treeview",
        )
        tree.heading("rank", text="#")
        tree.heading("name", text="PLAYER")
        tree.heading("class", text="CLASS")
        tree.heading("score", text="BEST SCORE")
        tree.column("rank", width=45, anchor="center")
        tree.column("name", width=210)
        tree.column("class", width=120, anchor="center")
        tree.column("score", width=110, anchor="e")
        tree.pack(padx=20, pady=10)

        leaders = database.leaderboard(10)
        for rank, player in enumerate(leaders, start=1):
            tag = "alternate" if rank % 2 == 0 else "normal"
            tree.insert(
                "",
                "end",
                values=(
                    rank,
                    f"{player.first_name} {player.last_name}",
                    player.class_name,
                    player.best_score,
                ),
                tags=(tag,),
            )

        tree.tag_configure("normal", background=WINDOW_BG, foreground=DARK_TEXT)
        tree.tag_configure("alternate", background=TREE_ALT_BG, foreground=DARK_TEXT)

        if not leaders:
            tk.Label(
                self,
                text="No saved scores yet.",
                font=("Arial", 11),
                fg=DARK_TEXT,
                bg=WINDOW_BG,
            ).pack(pady=(0, 8))

        ttk.Button(
            self,
            text="CLOSE",
            command=self.destroy,
            style="Game.TButton",
            cursor="hand2",
        ).pack(pady=(5, 20))


class Game2048App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("2048 - Python & SQL")
        self.configure(bg=WINDOW_BG)
        self.resizable(False, False)
        configure_ttk_styles(self)

        self._closing = False
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            self.createcommand("tk::mac::Quit", self.on_close)
        except tk.TclError:
            pass

        project_root = Path(__file__).resolve().parent.parent
        database_path = persistent_database_path(project_root)
        self.database = ScoreDatabase(
            db_path=database_path,
            schema_path=project_root / "sql" / "schema.sql",
        )

        self.player: Player | None = None
        self.board = Board()
        self.best_score = 0
        self.session_recorded = False
        self.animation_running = False
        self._won_dialog_shown = False

        self.score_var = tk.StringVar(value="0")
        self.best_var = tk.StringVar(value="0")
        self.player_var = tk.StringVar(value="")
        self.save_status_var = tk.StringVar(value="Progress is saved automatically.")

        self._build_ui()
        self._bind_keys()
        self.update_idletasks()
        self._center_window()

        self.deiconify()
        self.update_idletasks()
        dialog = PlayerDialog(self, self.database)
        self.wait_window(dialog)
        if dialog.player is None:
            super().destroy()
            return

        self.player = dialog.player
        self.best_score = dialog.player.best_score
        self.player_var.set(
            f"{dialog.player.first_name} {dialog.player.last_name} · "
            f"{dialog.player.class_name}"
        )
        self.best_var.set(str(self.best_score))
        self._restore_saved_game()

        self.lift()
        self.focus_force()
        self.render_board()

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=WINDOW_BG, padx=22, pady=18)
        outer.pack()

        header = tk.Frame(outer, bg=WINDOW_BG)
        header.pack(fill="x")

        tk.Label(
            header,
            text="2048",
            font=("Arial", 48, "bold"),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).pack(side="left")

        score_area = tk.Frame(header, bg=WINDOW_BG)
        score_area.pack(side="right")

        self._score_card(score_area, "SCORE", self.score_var).pack(
            side="left", padx=4
        )
        self._score_card(score_area, "BEST", self.best_var).pack(
            side="left", padx=4
        )

        tk.Label(
            outer,
            textvariable=self.player_var,
            font=("Arial", 11, "bold"),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
            anchor="w",
        ).pack(fill="x", pady=(4, 2))

        controls = tk.Frame(outer, bg=WINDOW_BG)
        controls.pack(fill="x", pady=(8, 12))

        tk.Label(
            controls,
            text="Join the numbers and get to the 2048 tile!",
            font=("Arial", 11),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).pack(side="left")

        ttk.Button(
            controls,
            text="NEW GAME",
            command=self.new_game,
            style="Game.TButton",
            cursor="hand2",
        ).pack(side="right", padx=(7, 0))

        ttk.Button(
            controls,
            text="LEADERBOARD",
            command=self.show_leaderboard,
            style="Game.TButton",
            cursor="hand2",
        ).pack(side="right")

        self.canvas = tk.Canvas(
            outer,
            width=BOARD_PIXELS,
            height=BOARD_PIXELS,
            bg=GRID_BG,
            highlightthickness=0,
        )
        self.canvas.pack()

        footer = tk.Frame(outer, bg=WINDOW_BG)
        footer.pack(fill="x", pady=(10, 0))

        tk.Label(
            footer,
            text="Use the arrow keys or W A S D to move.",
            font=("Arial", 10),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).pack(side="left")

        tk.Label(
            footer,
            textvariable=self.save_status_var,
            font=("Arial", 9, "bold"),
            fg=DARK_TEXT,
            bg=WINDOW_BG,
        ).pack(side="right")

    @staticmethod
    def _score_card(
        parent: tk.Misc,
        title: str,
        variable: tk.StringVar,
    ) -> tk.Frame:
        card = tk.Frame(parent, bg=GRID_BG, padx=14, pady=6)
        tk.Label(
            card,
            text=title,
            font=("Arial", 9, "bold"),
            fg="#eee4da",
            bg=GRID_BG,
        ).pack()
        tk.Label(
            card,
            textvariable=variable,
            font=("Arial", 18, "bold"),
            fg=LIGHT_TEXT,
            bg=GRID_BG,
        ).pack()
        return card

    def _bind_keys(self) -> None:
        mapping: dict[str, Direction] = {
            "Left": "left",
            "a": "left",
            "A": "left",
            "Right": "right",
            "d": "right",
            "D": "right",
            "Up": "up",
            "w": "up",
            "W": "up",
            "Down": "down",
            "s": "down",
            "S": "down",
        }
        for key, direction in mapping.items():
            self.bind(
                f"<KeyPress-{key}>",
                lambda _event, d=direction: self.handle_move(d),
            )

    def _center_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2 - 20)
        self.geometry(f"+{x}+{y}")

    def _restore_saved_game(self) -> None:
        if self.player is None:
            return

        saved = self.database.load_game_state(self.player.id)
        if saved is None:
            return

        try:
            self.board.set_grid(saved.grid)
        except ValueError:
            self.database.clear_game_state(self.player.id)
            return

        self.board.score = saved.score
        self.board.won = saved.won
        self.score_var.set(str(saved.score))
        self.best_score = max(self.best_score, saved.score)
        self.best_var.set(str(self.best_score))
        self.save_status_var.set("Saved game restored.")

        self.after(
            2200,
            lambda: self.save_status_var.set("Progress is saved automatically.")
            if self.winfo_exists()
            else None,
        )

    def _persist_progress(self) -> None:
        if self.player is None:
            return

        self.database.save_game_state(
            self.player.id,
            self.board.grid,
            self.board.score,
            self.board.won,
        )
        self.best_score = self.database.update_best_score(
            self.player.id,
            self.board.score,
        )
        self.best_var.set(str(self.best_score))
        self.save_status_var.set("Saved")

        self.after(
            900,
            lambda: self.save_status_var.set("Progress is saved automatically.")
            if self.winfo_exists()
            else None,
        )

    def handle_move(self, direction: Direction) -> None:
        if self.animation_running or self.player is None:
            return

        result = self.board.move(direction)
        if not result.moved:
            return

        self.session_recorded = False
        self.score_var.set(str(self.board.score))
        self._persist_progress()
        self.animate(result)

    def animate(self, result: MoveResult) -> None:
        changed = set(result.merged_cells)
        if result.new_tile is not None:
            changed.add(result.new_tile)

        if not changed:
            self.render_board()
            self._after_animation()
            return

        self.animation_running = True
        steps = iter(ANIMATION_STEPS)

        def next_frame() -> None:
            try:
                scale = next(steps)
            except StopIteration:
                self.animation_running = False
                self.render_board()
                self._after_animation()
                return

            self.render_board(animated_cells=changed, scale=scale)
            self.after(ANIMATION_DELAY_MS, next_frame)

        next_frame()

    def _after_animation(self) -> None:
        if self.board.won and not self._won_dialog_shown:
            self._won_dialog_shown = True
            messagebox.showinfo(
                "You win!",
                "You reached 2048! You can keep playing.",
                parent=self,
            )

        if self.board.is_game_over():
            self._complete_current_game()
            messagebox.showinfo(
                "Game over",
                f"No more moves are available.\n\nFinal score: {self.board.score}",
                parent=self,
            )

    def render_board(
        self,
        *,
        animated_cells: set[tuple[int, int]] | None = None,
        scale: float = 1.0,
    ) -> None:
        animated_cells = animated_cells or set()
        self.canvas.delete("all")

        for row in range(self.board.size):
            for col in range(self.board.size):
                value = self.board.grid[row][col]
                cell_scale = scale if (row, col) in animated_cells else 1.0
                self._draw_tile(row, col, value, cell_scale)

    def _draw_tile(self, row: int, col: int, value: int, scale: float) -> None:
        x1 = CELL_GAP + col * (CELL_SIZE + CELL_GAP)
        y1 = CELL_GAP + row * (CELL_SIZE + CELL_GAP)
        center_x = x1 + CELL_SIZE / 2
        center_y = y1 + CELL_SIZE / 2
        half = CELL_SIZE * scale / 2

        left = center_x - half
        top = center_y - half
        right = center_x + half
        bottom = center_y + half

        fill = TILE_COLORS.get(value, "#3c3a32")
        self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill=fill,
            outline=fill,
            width=0,
        )

        if value:
            text_color = TILE_TEXT_COLORS.get(value, LIGHT_TEXT)
            font_size = TILE_FONT_SIZES.get(value, 18)
            font_size = max(12, round(font_size * min(scale, 1.0)))
            self.canvas.create_text(
                center_x,
                center_y,
                text=str(value),
                fill=text_color,
                font=("Arial", font_size, "bold"),
            )

    def highest_tile(self) -> int:
        return max(max(row) for row in self.board.grid)

    def _complete_current_game(self) -> None:
        if self.session_recorded or self.player is None:
            return

        if self.board.score > 0:
            self.database.record_game(
                self.player.id,
                self.board.score,
                self.highest_tile(),
                self.board.won,
            )
        self.database.clear_game_state(self.player.id)
        self.best_score = max(self.best_score, self.board.score)
        self.best_var.set(str(self.best_score))
        self.session_recorded = True

    def new_game(self) -> None:
        if self.board.score > 0 and not self.board.is_game_over():
            should_restart = messagebox.askyesno(
                "Start a new game?",
                "Your current score will be saved in your history. Start a new game?",
                parent=self,
            )
            if not should_restart:
                return

        self._complete_current_game()
        self.board.reset()
        self.score_var.set("0")
        self.session_recorded = False
        self._won_dialog_shown = False
        if self.player is not None:
            self.database.clear_game_state(self.player.id)
        self.save_status_var.set("New game started.")
        self.render_board()
        self.focus_force()

    def show_leaderboard(self) -> None:
        LeaderboardDialog(self, self.database)

    def on_close(self) -> None:
        if self._closing:
            return
        self._closing = True

        try:
            if self.player is not None and not self.board.is_game_over():
                self._persist_progress()
            elif self.player is not None:
                self._complete_current_game()
        finally:
            super().destroy()
