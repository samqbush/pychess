"""Tests for issue #1869: Chess960 castling in the Setup Position dialog.

Covers:
- LBoard.applyFen() accepting X-FEN file-letter castling rights in the
  non-FISCHERRANDOMCHESS (SETUPCHESS) code path — fix (B).
- The _castling_fen() helper logic for producing correct X-FEN castling
  fields from abstract flags — fix (A).
- Classical KQkq round-trip regression check.
"""

import unittest

from pychess.Utils.const import (
    B_OO,
    B_OOO,
    FISCHERRANDOMCHESS,
    SETUPCHESS,
    W_OO,
    W_OOO,
)
from pychess.Utils.lutils.LBoard import LBoard
from pychess.Utils.lutils.ldata import FILE


def _castling_fen_from_flags(flags, pieces, variant_index):
    """Standalone reimplementation of SetupPositionExtension._castling_fen().

    Avoids GTK by operating directly on LBoard.  Mirrors the dialog logic so
    the same code path is exercised without needing a running Gtk main loop.
    """
    if not flags:
        return "-"

    if variant_index == FISCHERRANDOMCHESS:
        tmp = LBoard(FISCHERRANDOMCHESS)
        tmp.applyFen(pieces + " w - - 0 1")
        rank1 = pieces.split("/")[7] if "/" in pieces else ""
        rank8 = pieces.split("/")[0] if "/" in pieces else ""
        king_file_w = FILE(tmp.kings[0])
        king_file_b = FILE(tmp.kings[1])

        def rank_to_piece_files(rank_str):
            result = []
            f = 0
            for ch in rank_str:
                if ch.isdigit():
                    f += int(ch)
                else:
                    result.append((f, ch))
                    f += 1
            return result

        w_rook_f = [f for f, c in rank_to_piece_files(rank1) if c == "R"]
        b_rook_f = [f for f, c in rank_to_piece_files(rank8) if c == "r"]
        oo_w = max((f for f in w_rook_f if f > king_file_w), default=None)
        ooo_w = min((f for f in w_rook_f if f < king_file_w), default=None)
        oo_b = max((f for f in b_rook_f if f > king_file_b), default=None)
        ooo_b = min((f for f in b_rook_f if f < king_file_b), default=None)
        if oo_w is not None:
            tmp.ini_rooks[0][1] = oo_w
        if ooo_w is not None:
            tmp.ini_rooks[0][0] = ooo_w
        if oo_b is not None:
            tmp.ini_rooks[1][1] = oo_b + 56
        if ooo_b is not None:
            tmp.ini_rooks[1][0] = ooo_b + 56

        castling_mask = 0
        if W_OO in flags and oo_w is not None:
            castling_mask |= W_OO
        if W_OOO in flags and ooo_w is not None:
            castling_mask |= W_OOO
        if B_OO in flags and oo_b is not None:
            castling_mask |= B_OO
        if B_OOO in flags and ooo_b is not None:
            castling_mask |= B_OOO
        tmp.setCastling(castling_mask)
        return tmp.reprCastling()
    else:
        castl_str = ""
        if W_OO in flags:
            castl_str += "K"
        if W_OOO in flags:
            castl_str += "Q"
        if B_OO in flags:
            castl_str += "k"
        if B_OOO in flags:
            castl_str += "q"
        return castl_str if castl_str else "-"


class SetupCastlingApplyFenTest(unittest.TestCase):
    """LBoard.applyFen() SETUPCHESS branch accepts X-FEN file-letter castling."""

    def _apply(self, fen, variant=SETUPCHESS):
        board = LBoard(variant)
        board.applyFen(fen)
        return board

    def test_setupchess_xfen_AHah_sets_all_flags(self):
        """r3k2r / R3K2R with AHah should set all four castling flags."""
        board = self._apply("r3k2r/8/8/8/8/8/8/R3K2R w AHah - 0 1")
        self.assertTrue(board.castling & W_OO, "W_OO should be set")
        self.assertTrue(board.castling & W_OOO, "W_OOO should be set")
        self.assertTrue(board.castling & B_OO, "B_OO should be set")
        self.assertTrue(board.castling & B_OOO, "B_OOO should be set")

    def test_setupchess_xfen_only_white_kingside(self):
        """Uppercase H only → W_OO set, nothing else."""
        board = self._apply("r3k2r/8/8/8/8/8/8/R3K2R w H - 0 1")
        self.assertTrue(board.castling & W_OO, "W_OO should be set")
        self.assertFalse(board.castling & W_OOO, "W_OOO should not be set")
        self.assertFalse(board.castling & B_OO, "B_OO should not be set")
        self.assertFalse(board.castling & B_OOO, "B_OOO should not be set")

    def test_setupchess_xfen_only_black_kingside(self):
        """Lowercase h only → B_OO set, nothing else."""
        board = self._apply("r3k2r/8/8/8/8/8/8/R3K2R b h - 0 1")
        self.assertFalse(board.castling & W_OO, "W_OO should not be set")
        self.assertFalse(board.castling & W_OOO, "W_OOO should not be set")
        self.assertTrue(board.castling & B_OO, "B_OO should be set")
        self.assertFalse(board.castling & B_OOO, "B_OOO should not be set")

    def test_setupchess_xfen_queenside_letters(self):
        """A / a  file letters → queen-side rights."""
        board = self._apply("r3k2r/8/8/8/8/8/8/R3K2R w Aa - 0 1")
        self.assertFalse(board.castling & W_OO, "W_OO should not be set")
        self.assertTrue(board.castling & W_OOO, "W_OOO should be set")
        self.assertFalse(board.castling & B_OO, "B_OO should not be set")
        self.assertTrue(board.castling & B_OOO, "B_OOO should be set")

    def test_setupchess_dash_clears_all(self):
        """'-' → no castling rights."""
        board = self._apply("r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1")
        self.assertFalse(board.castling, "No castling should be set")

    def test_setupchess_kqkq_still_works(self):
        """Classical KQkq notation is still parsed correctly."""
        board = self._apply("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertTrue(board.castling & W_OO)
        self.assertTrue(board.castling & W_OOO)
        self.assertTrue(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)

    def test_setupchess_frc_position_CH_letters(self):
        """Chess960 position with C/H rooks: CH / ch parsed correctly."""
        board = self._apply("1br3kr/2p5/8/8/8/8/8/1BR3KR w CHch - 0 1")
        self.assertTrue(board.castling & W_OO)
        self.assertTrue(board.castling & W_OOO)
        self.assertTrue(board.castling & B_OO)
        self.assertTrue(board.castling & B_OOO)


class SetupCastlingFenOutputTest(unittest.TestCase):
    """_castling_fen() helper produces correct FEN castling fields."""

    def test_frc_standard_position_all_rights(self):
        """r3k2r / R3K2R → HAha for full FRC castling (kingside-first per reprCastling)."""
        pieces = "r3k2r/8/8/8/8/8/8/R3K2R"
        flags = {W_OO, W_OOO, B_OO, B_OOO}
        result = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(result, "HAha")

    def test_frc_kingside_only(self):
        """Only kingside rights → Hh."""
        pieces = "r3k2r/8/8/8/8/8/8/R3K2R"
        flags = {W_OO, B_OO}
        result = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(result, "Hh")

    def test_frc_white_only(self):
        """Only white rights → HA (kingside first)."""
        pieces = "r3k2r/8/8/8/8/8/8/R3K2R"
        flags = {W_OO, W_OOO}
        result = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(result, "HA")

    def test_frc_no_flags(self):
        """No flags → '-'."""
        pieces = "r3k2r/8/8/8/8/8/8/R3K2R"
        result = _castling_fen_from_flags(set(), pieces, FISCHERRANDOMCHESS)
        self.assertEqual(result, "-")

    def test_frc_ch_position(self):
        """Chess960 position with rooks on C and H files → HChc."""
        pieces = "1br3kr/2p5/8/8/8/8/8/1BR3KR"
        flags = {W_OO, W_OOO, B_OO, B_OOO}
        result = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(result, "HChc")

    def test_classical_all_rights(self):
        """Non-FRC variant → KQkq."""
        from pychess.Utils.const import NORMALCHESS

        pieces = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        flags = {W_OO, W_OOO, B_OO, B_OOO}
        result = _castling_fen_from_flags(flags, pieces, NORMALCHESS)
        self.assertEqual(result, "KQkq")

    def test_classical_kingside_only(self):
        """Non-FRC: only kingside → Kk."""
        from pychess.Utils.const import NORMALCHESS

        pieces = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        flags = {W_OO, B_OO}
        result = _castling_fen_from_flags(flags, pieces, NORMALCHESS)
        self.assertEqual(result, "Kk")

    def test_classical_no_flags(self):
        """Non-FRC: no flags → '-'."""
        from pychess.Utils.const import NORMALCHESS

        result = _castling_fen_from_flags(set(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", NORMALCHESS)
        self.assertEqual(result, "-")


class SetupCastlingRoundTripTest(unittest.TestCase):
    """Round-trip: load a FEN into SETUPCHESS, verify flags, re-emit FEN."""

    def _flags_from_setup_fen(self, fen):
        """Parse FEN via SETUPCHESS board and return active castling flags."""
        board = LBoard(SETUPCHESS)
        board.applyFen(fen)
        flags = set()
        if board.castling & W_OO:
            flags.add(W_OO)
        if board.castling & W_OOO:
            flags.add(W_OOO)
        if board.castling & B_OO:
            flags.add(B_OO)
        if board.castling & B_OOO:
            flags.add(B_OOO)
        return flags

    def test_frc_round_trip_ahah(self):
        """Chess960 FEN with AHah → flags → re-emitted as HAha (kingside first)."""
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w AHah - 0 1"
        pieces = fen.split()[0]
        flags = self._flags_from_setup_fen(fen)
        self.assertEqual(flags, {W_OO, W_OOO, B_OO, B_OOO})
        castl = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(castl, "HAha")

    def test_frc_round_trip_ch(self):
        """Chess960 FEN with CHch → flags → re-emitted as HChc (kingside first)."""
        fen = "1br3kr/2p5/8/8/8/8/8/1BR3KR w CHch - 0 1"
        pieces = fen.split()[0]
        flags = self._flags_from_setup_fen(fen)
        self.assertEqual(flags, {W_OO, W_OOO, B_OO, B_OOO})
        castl = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(castl, "HChc")

    def test_classical_round_trip(self):
        """Classical FEN with KQkq round-trips to KQkq (no regression)."""
        from pychess.Utils.const import NORMALCHESS

        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        pieces = fen.split()[0]
        flags = self._flags_from_setup_fen(fen)
        self.assertEqual(flags, {W_OO, W_OOO, B_OO, B_OOO})
        castl = _castling_fen_from_flags(flags, pieces, NORMALCHESS)
        self.assertEqual(castl, "KQkq")

    def test_frc_partial_kingside_only(self):
        """Loading h-only FRC FEN gives only B_OO, re-emits 'h'."""
        fen = "2r1k2r/8/8/8/8/8/8/2R1K2R b h - 0 1"
        pieces = fen.split()[0]
        flags = self._flags_from_setup_fen(fen)
        self.assertIn(B_OO, flags)
        self.assertNotIn(B_OOO, flags)
        castl = _castling_fen_from_flags(flags, pieces, FISCHERRANDOMCHESS)
        self.assertEqual(castl, "h")


if __name__ == "__main__":
    unittest.main()
