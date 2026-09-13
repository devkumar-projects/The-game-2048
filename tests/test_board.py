import random
import unittest

from game.board import Board


class BoardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board(rng=random.Random(0), start_tiles=False)

    def test_recursive_merge_simple_pair(self) -> None:
        merged, score, indices = self.board.merge_line([2, 2, 0, 0])
        self.assertEqual(merged, [4, 0, 0, 0])
        self.assertEqual(score, 4)
        self.assertEqual(indices, [0])

    def test_recursive_merge_does_not_double_merge(self) -> None:
        merged, score, indices = self.board.merge_line([2, 2, 2, 2])
        self.assertEqual(merged, [4, 4, 0, 0])
        self.assertEqual(score, 8)
        self.assertEqual(indices, [0, 1])

    def test_recursive_merge_chain(self) -> None:
        merged, score, indices = self.board.merge_line([4, 4, 8, 8])
        self.assertEqual(merged, [8, 16, 0, 0])
        self.assertEqual(score, 24)
        self.assertEqual(indices, [0, 1])

    def test_set_grid_rejects_invalid_tiles(self) -> None:
        with self.assertRaises(ValueError):
            self.board.set_grid(
                [
                    [2, 3, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ]
            )

    def test_merge_line_rejects_oversized_input(self) -> None:
        with self.assertRaises(ValueError):
            self.board.merge_line([2, 2, 2, 2, 2])

    def test_move_left(self) -> None:
        self.board.set_grid(
            [
                [2, 0, 2, 2],
                [4, 4, 8, 0],
                [0, 0, 0, 0],
                [2, 2, 4, 4],
            ]
        )
        result = self.board.move("left")
        self.assertTrue(result.moved)
        self.assertEqual(result.score_gained, 24)
        self.assertEqual(self.board.grid[0][0:2], [4, 2])
        self.assertEqual(self.board.grid[1][0:2], [8, 8])
        self.assertEqual(self.board.grid[3][0:2], [4, 8])

    def test_move_up(self) -> None:
        self.board.set_grid(
            [
                [2, 0, 2, 0],
                [2, 0, 2, 0],
                [4, 0, 4, 0],
                [4, 0, 4, 0],
            ]
        )
        result = self.board.move("up")
        self.assertTrue(result.moved)
        self.assertEqual(result.score_gained, 24)
        self.assertEqual(
            [self.board.grid[row][0] for row in range(2)],
            [4, 8],
        )

    def test_no_move_when_board_unchanged(self) -> None:
        self.board.set_grid(
            [
                [2, 4, 8, 16],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        )
        result = self.board.move("left")
        self.assertFalse(result.moved)
        self.assertIsNone(result.new_tile)

    def test_game_over_detection(self) -> None:
        self.board.set_grid(
            [
                [2, 4, 2, 4],
                [4, 2, 4, 2],
                [2, 4, 2, 4],
                [4, 2, 4, 2],
            ]
        )
        self.assertTrue(self.board.is_game_over())

    def test_not_game_over_when_merge_available(self) -> None:
        self.board.set_grid(
            [
                [2, 2, 4, 8],
                [4, 8, 16, 32],
                [8, 16, 32, 64],
                [16, 32, 64, 128],
            ]
        )
        self.assertFalse(self.board.is_game_over())


if __name__ == "__main__":
    unittest.main()
