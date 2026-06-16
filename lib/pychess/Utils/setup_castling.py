"""Pure helper for building the FEN castling field from a setup-position board.

Kept in a GTK-free module so it can be unit-tested without a running display.
"""

from pychess.Utils.const import FISCHERRANDOMCHESS, WHITE, BLACK, ROOK, reprFile
from pychess.Utils.lutils.ldata import FILE
from pychess.Utils.lutils.bitboard import bitPosArray


def castling_field_for_setup(variant_index, woo, wooo, boo, booo, lboard):
    """Return the FEN castling field string for a setup-position board.

    Parameters
    ----------
    variant_index : int
        The game variant constant (e.g. NORMALCHESS or FISCHERRANDOMCHESS).
    woo, wooo, boo, booo : bool
        Whether white kingside, white queenside, black kingside, and black
        queenside castling rights are currently enabled in the dialog.
    lboard : LBoard
        The current setup board (may be a SETUPCHESS board even for FRC games).

    For Fischer Random the castling string uses rook-file letters derived from
    the actual piece positions on the back ranks, e.g. ``"HAha"`` when the
    rooks are on the h- and a-files.  The ordering matches LBoard.reprCastling():
    W_OO first, W_OOO second, B_OO third, B_OOO fourth.

    For all other variants classical ``KQkq`` notation is returned.
    """
    if not (woo or wooo or boo or booo):
        return "-"

    if variant_index == FISCHERRANDOMCHESS:
        wking_file = FILE(lboard.kings[WHITE])
        bking_file = FILE(lboard.kings[BLACK])
        white_rooks = lboard.boards[WHITE][ROOK]
        black_rooks = lboard.boards[BLACK][ROOK]
        strs = []

        # W_OO: rightmost white rook strictly right of the white king (rank 1)
        if woo:
            for f in range(7, wking_file, -1):
                if white_rooks & bitPosArray[f]:
                    strs.append(reprFile[f].upper())
                    break

        # W_OOO: leftmost white rook strictly left of the white king (rank 1)
        if wooo:
            for f in range(0, wking_file):
                if white_rooks & bitPosArray[f]:
                    strs.append(reprFile[f].upper())
                    break

        # B_OO: rightmost black rook strictly right of the black king (rank 8)
        if boo:
            for f in range(7, bking_file, -1):
                if black_rooks & bitPosArray[56 + f]:
                    strs.append(reprFile[f])
                    break

        # B_OOO: leftmost black rook strictly left of the black king (rank 8)
        if booo:
            for f in range(0, bking_file):
                if black_rooks & bitPosArray[56 + f]:
                    strs.append(reprFile[f])
                    break

        return "".join(strs) if strs else "-"
    else:
        strs = []
        if woo:
            strs.append("K")
        if wooo:
            strs.append("Q")
        if boo:
            strs.append("k")
        if booo:
            strs.append("q")
        return "".join(strs)
