from pathlib import Path
import tempfile
import unittest

from game.database import ScoreDatabase


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parent.parent
        self.database = ScoreDatabase(
            db_path=Path(self.temp_dir.name) / "test_scores.db",
            schema_path=root / "sql" / "schema.sql",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_and_reuse_player(self) -> None:
        first = self.database.get_or_create_player("Ada", "Lovelace", "CS1")
        second = self.database.get_or_create_player("Ada", "Lovelace", "CS1")
        self.assertEqual(first.id, second.id)

    def test_best_score_only_increases(self) -> None:
        player = self.database.get_or_create_player("Alan", "Turing", "AI")
        self.assertEqual(self.database.update_best_score(player.id, 120), 120)
        self.assertEqual(self.database.update_best_score(player.id, 80), 120)

    def test_record_game_updates_leaderboard(self) -> None:
        player = self.database.get_or_create_player("Grace", "Hopper", "CS2")
        self.database.record_game(player.id, 512, 64, False)
        leaders = self.database.leaderboard()
        self.assertEqual(leaders[0].best_score, 512)

    def test_saved_game_round_trip(self) -> None:
        player = self.database.get_or_create_player("Katherine", "Johnson", "MATH")
        grid = [
            [2, 4, 0, 0],
            [8, 16, 0, 0],
            [0, 0, 32, 0],
            [0, 0, 0, 64],
        ]
        self.database.save_game_state(player.id, grid, 740, False)

        restored = self.database.load_game_state(player.id)
        self.assertIsNotNone(restored)
        assert restored is not None
        self.assertEqual(restored.score, 740)
        self.assertEqual(restored.grid[0], (2, 4, 0, 0))
        self.assertEqual(restored.grid[3][3], 64)

    def test_invalid_saved_grid_is_discarded(self) -> None:
        player = self.database.get_or_create_player("Katherine", "Johnson", "MATH")
        self.database.save_game_state(
            player.id,
            [[2, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            740,
            False,
        )
        with self.database._connect() as connection:
            connection.execute(
                "UPDATE saved_games SET grid_json = ? WHERE player_id = ?",
                ("[[2,3,0,0]]", player.id),
            )
        self.assertIsNone(self.database.load_game_state(player.id))

    def test_clear_saved_game(self) -> None:
        player = self.database.get_or_create_player("Dorothy", "Vaughan", "CS")
        self.database.save_game_state(
            player.id,
            [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            2,
            False,
        )
        self.database.clear_game_state(player.id)
        self.assertIsNone(self.database.load_game_state(player.id))


if __name__ == "__main__":
    unittest.main()
