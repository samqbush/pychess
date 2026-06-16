"""Regression tests for Chess960 (Fischer Random) castling field generation
in the setup-position dialog.

These tests exercise the pure helper _castling_field_for_setup() directly,
without requiring a running GTK dialog.  The helper must emit file-letter
notation (e.g. "HAha") for Fischer Random positions, and classical KQkq
notation for normal chess, based only on the current board geometry and the
caller-supplied castling-right flags.
"""

import unittest

from pychess.Utils.const import (
    FISCHERRANDOMCHESS,
    NORMALCHESS,
    SETUPCHESS,
    WHITE,
    BLACK,
)
from pychess.Utils.lutils.LBoard import LBoard
from pychess.Utils.setup_castling import castling_field_for_setup as _castling_field_for_setup


def _setup_board(fenstr):
    """Return a SETUPCHESS LBoard with the given FEN applied.

    This mirrors the production path: the dialog always uses a SETUPCHESS
    board even when the user selected Fischer Random as the game variant.
    """
    board = LBoard(SETUPCHESS)
    board.applyFen(fenstr)
    return board


class FRCSetupCastlingTestCase(unittest.TestCase):
    """Verify _castling_field_for_setup produces correct FEN castling strings."""

    def test_standard_frc_rooks_on_a_h_full_rights(self):
        """Full rights, rooks on a/h files: emits file letters not KQkq."""
        # Classic FRC starting layout: rooks at a1/h1, king at e1.
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, True, True, True, True, board
        )
        # W_OO = kingside = H, W_OOO = queenside = A; same lowercase for black.
        self.assertEqual(result, "HAha")
        self.assertNotIn("K", result)
        self.assertNotIn("Q", result)

    def test_standard_frc_rooks_on_a_h_white_only(self):
        """White-only rights with rooks at a1/h1: emits uppercase file letters."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w AH - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, True, True, False, False, board
        )
        self.assertEqual(result, "HA")

    def test_non_standard_rook_positions(self):
        """Non-a/h rooks: helper finds correct files from board geometry."""
        # Position from frc_castling.py test data: rooks at c1/h1, king at g1.
        board = _setup_board("1br3kr/2p5/8/8/8/8/8/1BR3KR w CH - 0 2")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, True, True, True, True, board
        )
        # Kingside W_OO=H (right of king at g1), queenside W_OOO=C (left of king at g1).
        # Same logic for black (king at g8, rooks at c8/h8).
        # Order: W_OO=H, W_OOO=C, B_OO=h (rightmost right of king at g8 = h8),
        # B_OOO=c (leftmost left of king at g8 = c8).
        self.assertEqual(result, "HChc")

    def test_kingside_only_rights(self):
        """Only kingside rights enabled: only kingside rook file emitted."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w AH - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, True, False, False, False, board
        )
        self.assertEqual(result, "H")

    def test_queenside_only_rights(self):
        """Only queenside rights enabled: only queenside rook file emitted."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w AH - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, False, True, False, False, board
        )
        self.assertEqual(result, "A")

    def test_no_rights_returns_dash(self):
        """No castling rights enabled: returns '-'."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, False, False, False, False, board
        )
        self.assertEqual(result, "-")

    def test_normal_chess_full_rights(self):
        """Normal chess emits classical KQkq notation."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        result = _castling_field_for_setup(
            NORMALCHESS, True, True, True, True, board
        )
        self.assertEqual(result, "KQkq")

    def test_normal_chess_partial_rights(self):
        """Normal chess partial rights emits only the enabled letters."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w KQ - 0 1")
        result = _castling_field_for_setup(
            NORMALCHESS, True, True, False, False, board
        )
        self.assertEqual(result, "KQ")

    def test_imported_frc_start_position_ah(self):
        """Loaded FRC start FEN with AH castling round-trips correctly."""
        # Simulate loading a FRC FEN that already uses file-letter notation.
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w AH - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, True, True, False, False, board
        )
        self.assertIn("H", result)
        self.assertIn("A", result)
        self.assertNotIn("K", result)
        self.assertNotIn("Q", result)

    def test_frc_black_only_rights(self):
        """Black-only FRC rights: emits lowercase file letters only."""
        board = _setup_board("r3k2r/8/8/8/8/8/8/R3K2R w ah - 0 1")
        result = _castling_field_for_setup(
            FISCHERRANDOMCHESS, False, False, True, True, board
        )
        self.assertEqual(result, "ha")


if __name__ == "__main__":
    unittest.main()
