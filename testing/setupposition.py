import unittest

from pychess.Utils.const import FISCHERRANDOMCHESS, NORMALCHESS, W_OO, W_OOO, B_OO, B_OOO
from pychess.widgets.newGameDialog import SetupPositionExtension


class SetupPositionTestCase(unittest.TestCase):
    def test_chess960_castling_uses_rook_files(self):
        pieces = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        castling = W_OO | W_OOO | B_OO | B_OOO

        self.assertEqual(
            SetupPositionExtension._get_castling_fen(
                pieces, FISCHERRANDOMCHESS, castling
            ),
            "HAha",
        )

    def test_chess960_custom_rook_files_follow_board_layout(self):
        pieces = "1br3kr/8/8/8/8/8/8/1BR3KR"
        castling = W_OO | W_OOO | B_OO | B_OOO

        self.assertEqual(
            SetupPositionExtension._get_castling_fen(
                pieces, FISCHERRANDOMCHESS, castling
            ),
            "HChc",
        )

    def test_standard_castling_keeps_classical_notation(self):
        pieces = "r3k2r/8/8/8/8/8/8/R3K2R"
        castling = W_OO | W_OOO | B_OO | B_OOO

        self.assertEqual(
            SetupPositionExtension._get_castling_fen(pieces, NORMALCHESS, castling),
            "KQkq",
        )


if __name__ == "__main__":
    unittest.main()