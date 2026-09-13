from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Sequence

from .constants import BOARD_SIZE


@dataclass(frozen=True)
class Player:
    id: int
    first_name: str
    last_name: str
    class_name: str
    best_score: int


@dataclass(frozen=True)
class SavedGame:
    player_id: int
    grid: tuple[tuple[int, ...], ...]
    score: int
    won: bool


class ScoreDatabase:
    def __init__(
        self,
        db_path: str | Path = "scores.db",
        schema_path: str | Path | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.schema_path = (
            Path(schema_path)
            if schema_path is not None
            else Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        schema = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.executescript(schema)

    @staticmethod
    def _clean(value: str, field_name: str) -> str:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError(f"{field_name} is required.")
        if len(cleaned) > 80:
            raise ValueError(f"{field_name} is too long.")
        return cleaned

    def get_or_create_player(
        self,
        first_name: str,
        last_name: str,
        class_name: str,
    ) -> Player:
        first_name = self._clean(first_name, "First name")
        last_name = self._clean(last_name, "Last name")
        class_name = self._clean(class_name, "Class")

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO players (first_name, last_name, class_name)
                VALUES (?, ?, ?)
                ON CONFLICT(first_name, last_name, class_name) DO NOTHING
                """,
                (first_name, last_name, class_name),
            )
            row = connection.execute(
                """
                SELECT id, first_name, last_name, class_name, best_score
                FROM players
                WHERE first_name = ? AND last_name = ? AND class_name = ?
                """,
                (first_name, last_name, class_name),
            ).fetchone()

        if row is None:
            raise RuntimeError("Unable to create or load player.")
        return self._row_to_player(row)

    def get_player(self, player_id: int) -> Player | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, first_name, last_name, class_name, best_score
                FROM players
                WHERE id = ?
                """,
                (player_id,),
            ).fetchone()
        return self._row_to_player(row) if row else None

    def update_best_score(self, player_id: int, score: int) -> int:
        score = max(0, int(score))
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE players
                SET best_score = MAX(best_score, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (score, player_id),
            )
            row = connection.execute(
                "SELECT best_score FROM players WHERE id = ?",
                (player_id,),
            ).fetchone()

        if row is None:
            raise ValueError("Unknown player.")
        return int(row["best_score"])

    @staticmethod
    def _normalise_grid(grid: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
        try:
            normalised = tuple(
                tuple(int(value) for value in row)
                for row in grid
            )
        except (TypeError, ValueError):
            raise ValueError("Saved grid must contain integer tiles.") from None

        if len(normalised) != BOARD_SIZE or any(
            len(row) != BOARD_SIZE for row in normalised
        ):
            raise ValueError(f"Saved grid must be {BOARD_SIZE}x{BOARD_SIZE}.")
        if any(
            value < 0 or (value != 0 and (value & (value - 1)) != 0)
            for row in normalised
            for value in row
        ):
            raise ValueError("Saved grid tiles must be zero or powers of two.")
        return normalised

    def save_game_state(
        self,
        player_id: int,
        grid: Sequence[Sequence[int]],
        score: int,
        won: bool,
    ) -> None:
        normalised_grid = self._normalise_grid(grid)
        grid_json = json.dumps(
            [list(row) for row in normalised_grid],
            separators=(",", ":"),
        )
        score = max(0, int(score))

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO saved_games (player_id, grid_json, score, won)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                    grid_json = excluded.grid_json,
                    score = excluded.score,
                    won = excluded.won,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (player_id, grid_json, score, int(bool(won))),
            )
            connection.execute(
                """
                UPDATE players
                SET best_score = MAX(best_score, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (score, player_id),
            )

    def load_game_state(self, player_id: int) -> SavedGame | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT player_id, grid_json, score, won
                FROM saved_games
                WHERE player_id = ?
                """,
                (player_id,),
            ).fetchone()

        if row is None:
            return None

        try:
            decoded = json.loads(str(row["grid_json"]))
            grid = self._normalise_grid(decoded)
        except (TypeError, ValueError, json.JSONDecodeError):
            self.clear_game_state(player_id)
            return None

        return SavedGame(
            player_id=int(row["player_id"]),
            grid=grid,
            score=max(0, int(row["score"])),
            won=bool(row["won"]),
        )

    def clear_game_state(self, player_id: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM saved_games WHERE player_id = ?",
                (player_id,),
            )

    def record_game(
        self,
        player_id: int,
        score: int,
        highest_tile: int,
        won: bool,
    ) -> None:
        score = max(0, int(score))
        highest_tile = max(0, int(highest_tile))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO games (player_id, score, highest_tile, won)
                VALUES (?, ?, ?, ?)
                """,
                (player_id, score, highest_tile, int(bool(won))),
            )
            connection.execute(
                """
                UPDATE players
                SET best_score = MAX(best_score, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (score, player_id),
            )

    def leaderboard(self, limit: int = 10) -> list[Player]:
        limit = max(1, min(int(limit), 100))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, first_name, last_name, class_name, best_score
                FROM players
                ORDER BY best_score DESC, updated_at ASC, last_name ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_player(row) for row in rows]

    @staticmethod
    def _row_to_player(row: sqlite3.Row) -> Player:
        return Player(
            id=int(row["id"]),
            first_name=str(row["first_name"]),
            last_name=str(row["last_name"]),
            class_name=str(row["class_name"]),
            best_score=int(row["best_score"]),
        )
