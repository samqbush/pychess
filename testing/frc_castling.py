import unittest

from pychess.Utils.const import (
    A1,
    A8,
    C1,
    C8,
    E1,
    E8,
    G1,
    G8,
    H1,
    H8,
    FISCHERRANDOMCHESS,
    SETUPCHESS,
    KING_CASTLE,
    QUEEN_CASTLE,
    W_OO,
    W_OOO,
    B_OO,
    B_OOO,
)
from pychess.Utils.lutils.LBoard import LBoard
from pychess.Utils.lutils.lmove import parseAN
from pychess.Utils.lutils.lmovegen import genCastles, newMove

# TODO: add more test data
data = (
    (
        "r3k2r/8/8/8/8/8/8/R3K2R w AH - 0 1",
        [(E1, H1, KING_CASTLE), (E1, A1, QUEEN_CASTLE)],
    ),
    (
        "r3k2r/8/8/8/8/8/8/R3K2R b ah - 0 1",
        [(E8, H8, KING_CASTLE), (E8, A8, QUEEN_CASTLE)],
    ),
    (
        "1br3kr/2p5/8/8/8/8/8/1BR3KR w CH - 0 2",
        [(G1, H1, KING_CASTLE), (G1, C1, QUEEN_CASTLE)],
    ),
    (
        "1br3kr/2p5/8/8/8/8/8/1BR3KR b ch - 0 2",
        [(G8, H8, KING_CASTLE), (G8, C8, QUEEN_CASTLE)],
    ),
    ("2r1k2r/8/8/8/8/8/8/2R1K2R w H - 0 1", [(E1, H1, KING_CASTLE)]),
    ("2r1k2r/8/8/8/8/8/8/2R1K2R b h - 0 1", [(E8, H8, KING_CASTLE)]),
    ("3rk1qr/8/8/8/8/8/8/3RK1QR w - - 0 1", []),
    ("3rk1qr/8/8/8/8/8/8/3RK1QR b - - 0 1", []),
)


class FRCCastlingTestCase(unittest.TestCase):
    def testFRCCastling(self):
        """Testing FRC castling movegen"""
        print()

        for fen, castles in data:
            print(fen)
            board = LBoard(FISCHERRANDOMCHESS)
            board.applyFen(fen)
            # print board
            moves = [move for move in genCastles(board)]
            self.assertEqual(len(moves), len(castles))
            for i, castle in enumerate(castles):
                kfrom, kto, flag = castle
                self.assertEqual(moves[i], newMove(kfrom, kto, flag))

    def testFRCCastlingUCI(self):
        """Testing UCI engine FRC castling move"""
        print()

        fen = "rbq1krb1/pp1pp1pp/2p1n3/5p2/2PP1P1n/4B1N1/PP2P1PP/RBQNKR2 w FAfa - 2 6"
        print(fen)
        board = LBoard(FISCHERRANDOMCHESS)
        board.applyFen(fen)
        # print board
        moves = [move for move in genCastles(board)]
        self.assertTrue(parseAN(board, "e1g1") in moves)


class SetupChessFileCastlingTestCase(unittest.TestCase):
    """Tests for LBoard.applyFen() SETUPCHESS + X-FEN file-letter castling (issue #1869)."""

    def _load(self, fen):
        board = LBoard(SETUPCHESS)
        board.applyFen(fen)
        return board

    def test_classical_kqkq_unchanged(self):
        """Classical KQkq still parsed correctly in SETUPCHESS."""
        board = self._load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        self.assertTrue(board.castling & W_OO)
        self.assertTrue(board.castling & W_OOO)
        self.assertTrue(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)

    def test_file_letters_full(self):
        """Full AHah file-letter castling parsed correctly in SETUPCHESS."""
        board = self._load("r3k2r/8/8/8/8/8/8/R3K2R w AHah - 0 1")
        self.assertTrue(board.castling & W_OO, "W_OO should be set for H")
        self.assertTrue(board.castling & W_OOO, "W_OOO should be set for A")
        self.assertTrue(board.castling & B_OO, "B_OO should be set for h")
        self.assertTrue(board.castling & B_OOO, "B_OOO should be set for a")

    def test_file_letters_partial_kingside_only(self):
        """Only kingside file letters set W_OO/B_OO in SETUPCHESS."""
        board = self._load("2r1k2r/8/8/8/8/8/8/2R1K2R w Hh - 0 1")
        self.assertTrue(board.castling & W_OO)
        self.assertFalse(board.castling & W_OOO)
        self.assertTrue(board.castling & B_OO)
        self.assertFalse(board.castling & B_OOO)

    def test_file_letters_partial_queenside_only(self):
        """Only queenside file letters set W_OOO/B_OOO in SETUPCHESS."""
        board = self._load("r3k3/8/8/8/8/8/8/R3K3 w Aa - 0 1")
        self.assertFalse(board.castling & W_OO)
        self.assertTrue(board.castling & W_OOO)
        self.assertFalse(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)

    def test_no_castling(self):
        """Dash castling field sets castling to 0 in SETUPCHESS."""
        board = self._load("r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1")
        self.assertEqual(board.castling, 0)

    def test_non_ah_frc_position(self):
        """Non-standard FRC file letters (e.g. CH/ch) parsed correctly in SETUPCHESS."""
        # King on g1/g8, rooks on c1/h1 and c8/h8
        board = self._load("1br3kr/2p5/8/8/8/8/2P5/1BR3KR w CHch - 0 1")
        self.assertTrue(board.castling & W_OO, "H > G king, so W_OO")
        self.assertTrue(board.castling & W_OOO, "C < G king, so W_OOO")
        self.assertTrue(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)

    def test_reprCastling_roundtrip_via_frc_board(self):
        """FRC LBoard.reprCastling() round-trips AHah position consistently."""
        board = LBoard(FISCHERRANDOMCHESS)
        board.applyFen("r3k2r/8/8/8/8/8/8/R3K2R w AHah - 0 1")
        # All four castling rights should be set
        self.assertTrue(board.castling & W_OO)
        self.assertTrue(board.castling & W_OOO)
        self.assertTrue(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)
        # reprCastling should produce a non-empty result
        result = board.reprCastling()
        self.assertNotEqual(result, "-")
        self.assertIn("H", result)
        self.assertIn("A", result)
        self.assertIn("h", result)
        self.assertIn("a", result)


if __name__ == "__main__":
    unittest.main()
