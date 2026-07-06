from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, Literal, Sequence

from .constants import BOARD_SIZE, WINNING_TILE

Direction = Literal["left", "right", "up", "down"]


@dataclass(frozen=True)
class MoveResult:
    moved: bool
    score_gained: int
    merged_cells: tuple[tuple[int, int], ...]
    new_tile: tuple[int, int] | None


class Board:
    """Matrix-based 2048 engine.

    The merge itself is intentionally recursive. A line is compressed,
    recursively merged from left to right, then padded back to board size.
    """

    def __init__(
        self,
        size: int = BOARD_SIZE,
        *,
        rng: random.Random | None = None,
        start_tiles: bool = True,
    ) -> None:
        if size < 2:
            raise ValueError("Board size must be at least 2.")
        self.size = size
        self.rng = rng or random.Random()
        self.grid: list[list[int]] = [
            [0 for _ in range(size)] for _ in range(size)
        ]
        self.score = 0
        self.won = False

        if start_tiles:
            self.spawn_random_tile()
            self.spawn_random_tile()

    def reset(self) -> None:
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.won = False
        self.spawn_random_tile()
        self.spawn_random_tile()

    def set_grid(self, rows: Sequence[Sequence[int]]) -> None:
        if len(rows) != self.size or any(len(row) != self.size for row in rows):
            raise ValueError(f"Grid must be {self.size}x{self.size}.")
        self.grid = [list(map(int, row)) for row in rows]
        self.won = any(
            value >= WINNING_TILE for row in self.grid for value in row
        )

    def empty_cells(self) -> list[tuple[int, int]]:
        return [
            (row, col)
            for row in range(self.size)
            for col in range(self.size)
            if self.grid[row][col] == 0
        ]

    def spawn_random_tile(self) -> tuple[int, int] | None:
        empty = self.empty_cells()
        if not empty:
            return None

        row, col = self.rng.choice(empty)
        self.grid[row][col] = 4 if self.rng.random() < 0.10 else 2
        return row, col

    @staticmethod
    def _recursive_merge(values: Sequence[int]) -> tuple[list[int], int, list[int]]:
        """Recursively merge one compressed line.

        Returns:
            merged values, score gained, indices of newly merged values.
        """
        if not values:
            return [], 0, []

        if len(values) >= 2 and values[0] == values[1]:
            merged_value = values[0] * 2
            tail, tail_score, tail_indices = Board._recursive_merge(values[2:])
            shifted_indices = [index + 1 for index in tail_indices]
            return (
                [merged_value] + tail,
                merged_value + tail_score,
                [0] + shifted_indices,
            )

        tail, tail_score, tail_indices = Board._recursive_merge(values[1:])
        shifted_indices = [index + 1 for index in tail_indices]
        return [values[0]] + tail, tail_score, shifted_indices

    def merge_line(self, line: Iterable[int]) -> tuple[list[int], int, list[int]]:
        compressed = [value for value in line if value != 0]
        merged, score_gained, merged_indices = self._recursive_merge(compressed)
        merged.extend([0] * (self.size - len(merged)))
        return merged, score_gained, merged_indices

    def _move_left(self) -> tuple[list[list[int]], int, list[tuple[int, int]]]:
        new_grid: list[list[int]] = []
        total_gain = 0
        merged_cells: list[tuple[int, int]] = []

        for row_index, row in enumerate(self.grid):
            merged, gain, merged_indices = self.merge_line(row)
            new_grid.append(merged)
            total_gain += gain
            merged_cells.extend((row_index, col) for col in merged_indices)

        return new_grid, total_gain, merged_cells

    def _move_right(self) -> tuple[list[list[int]], int, list[tuple[int, int]]]:
        new_grid: list[list[int]] = []
        total_gain = 0
        merged_cells: list[tuple[int, int]] = []

        for row_index, row in enumerate(self.grid):
            merged, gain, merged_indices = self.merge_line(reversed(row))
            restored = list(reversed(merged))
            new_grid.append(restored)
            total_gain += gain
            merged_cells.extend(
                (row_index, self.size - 1 - col) for col in merged_indices
            )

        return new_grid, total_gain, merged_cells

    def _move_up(self) -> tuple[list[list[int]], int, list[tuple[int, int]]]:
        new_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        total_gain = 0
        merged_cells: list[tuple[int, int]] = []

        for col in range(self.size):
            column = [self.grid[row][col] for row in range(self.size)]
            merged, gain, merged_indices = self.merge_line(column)
            total_gain += gain
            for row, value in enumerate(merged):
                new_grid[row][col] = value
            merged_cells.extend((row, col) for row in merged_indices)

        return new_grid, total_gain, merged_cells

    def _move_down(self) -> tuple[list[list[int]], int, list[tuple[int, int]]]:
        new_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        total_gain = 0
        merged_cells: list[tuple[int, int]] = []

        for col in range(self.size):
            column = [self.grid[row][col] for row in reversed(range(self.size))]
            merged, gain, merged_indices = self.merge_line(column)
            restored = list(reversed(merged))
            total_gain += gain
            for row, value in enumerate(restored):
                new_grid[row][col] = value
            merged_cells.extend(
                (self.size - 1 - row, col) for row in merged_indices
            )

        return new_grid, total_gain, merged_cells

    def move(self, direction: Direction) -> MoveResult:
        movers = {
            "left": self._move_left,
            "right": self._move_right,
            "up": self._move_up,
            "down": self._move_down,
        }
        if direction not in movers:
            raise ValueError(f"Unsupported direction: {direction}")

        old_grid = [row[:] for row in self.grid]
        new_grid, score_gained, merged_cells = movers[direction]()
        moved = new_grid != old_grid

        if not moved:
            return MoveResult(False, 0, tuple(), None)

        self.grid = new_grid
        self.score += score_gained
        self.won = self.won or any(
            value >= WINNING_TILE for row in self.grid for value in row
        )
        new_tile = self.spawn_random_tile()
        return MoveResult(
            True,
            score_gained,
            tuple(merged_cells),
            new_tile,
        )

    def can_move(self) -> bool:
        if self.empty_cells():
            return True

        for row in range(self.size):
            for col in range(self.size):
                value = self.grid[row][col]
                if col + 1 < self.size and self.grid[row][col + 1] == value:
                    return True
                if row + 1 < self.size and self.grid[row + 1][col] == value:
                    return True
        return False

    def is_game_over(self) -> bool:
        return not self.can_move()
