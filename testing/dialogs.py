import asyncio
import unittest
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from pychess.Utils.const import FEN_START, NORMALCHESS
from pychess.Players.engineNest import discoverer
from pychess.System import uistuff, cancel_all_tasks
from pychess.widgets import gamewidget
from pychess.widgets import enginesDialog
from pychess.widgets import newGameDialog
from pychess.widgets.newGameDialog import COPY, CLEAR, PASTE, INITIAL
from pychess.widgets import preferencesDialog
from pychess.widgets.discovererDialog import DiscovererDialog
from pychess.perspectives.games import Games
from pychess.perspectives.welcome import Welcome
from pychess.perspectives import perspective_manager

discoverer.pre_discover()


class DialogTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        widgets = uistuff.GladeWidgets("PyChess.glade")
        gamewidget.setWidgets(widgets)
        perspective_manager.set_widgets(widgets)

        self.welcome_persp = Welcome()
        perspective_manager.add_perspective(self.welcome_persp)

        self.games_persp = Games()
        perspective_manager.add_perspective(self.games_persp)

    async def asyncTearDown(self):
        for gmwidg in self.games_persp.gamewidgets:
            gmwidg.gamemodel.terminate()
        self.games_persp.gamewidgets.clear()
        await cancel_all_tasks()

    async def test0(self):
        """Open engines dialogs"""

        # engines dialog
        widgets = gamewidget.getWidgets()
        enginesDialog.run(widgets)
        engines = [item[1] for item in enginesDialog.engine_dialog.allstore]
        self.assertTrue("PyChess.py" in engines)

        widgets["manage_engines_dialog"].hide()

    async def test1(self):
        """Open new game dialog"""

        dialog = newGameDialog.NewGameMode()

        def on_gmwidg_created(persp, gmwidg, event):
            event.set()

        event = asyncio.Event()
        self.games_persp.connect("gmwidg_created", on_gmwidg_created, event)

        dialog.run()
        dialog.widgets["newgamedialog"].response(Gtk.ResponseType.OK)

        await asyncio.wait_for(event.wait(), timeout=5)

        newGameDialog.NewGameMode.widgets["newgamedialog"].hide()

    async def test2(self):
        """Open setup position dialog"""

        dialog = newGameDialog.SetupPositionExtension()

        def on_gmwidg_created(persp, gmwidg, event):
            event.set()

        event = asyncio.Event()
        self.games_persp.connect("gmwidg_created", on_gmwidg_created, event)

        dialog.run(FEN_START, NORMALCHESS)
        dialog.widgets["newgamedialog"].response(INITIAL)
        dialog.widgets["newgamedialog"].response(COPY)
        dialog.widgets["newgamedialog"].response(CLEAR)
        dialog.widgets["newgamedialog"].response(PASTE)
        dialog.widgets["newgamedialog"].response(Gtk.ResponseType.OK)

        await asyncio.wait_for(event.wait(), timeout=5)

        newGameDialog.NewGameMode.widgets["newgamedialog"].hide()

    @unittest.skipIf(
        sys.platform == "win32",
        "Windows produces TypeError: could not get a reference to type class\n"
        + "on line: cls.sourcebuffer = GtkSource.Buffer()",
    )
    async def test3(self):
        """Start a new game from enter notation dialog"""

        dialog = newGameDialog.EnterNotationExtension()

        def on_gmwidg_created(persp, gmwidg, event):
            event.set()

        event = asyncio.Event()
        self.games_persp.connect("gmwidg_created", on_gmwidg_created, event)

        dialog.run()
        dialog.sourcebuffer.set_text("1. f3 e5 2. g4 Qh4")
        dialog.widgets["newgamedialog"].response(Gtk.ResponseType.OK)

        await asyncio.wait_for(event.wait(), timeout=5)

        # Show the firs move of the game
        def on_shown_changed(view, shown, event):
            if shown == 1:
                event.set()

        gmwidg = self.games_persp.gamewidgets.pop()
        view = gmwidg.board.view
        board = gmwidg.gamemodel.boards[1]

        event = asyncio.Event()
        view.connect("shownChanged", on_shown_changed, event)

        view.setShownBoard(board)

        await asyncio.wait_for(event.wait(), timeout=5)

        newGameDialog.NewGameMode.widgets["newgamedialog"].hide()

    async def test4(self):
        """Open preferences dialog"""

        widgets = gamewidget.getWidgets()
        preferencesDialog.run(widgets)

        notebook = widgets["preferences_notebook"]
        self.assertIsNotNone(preferencesDialog.general_tab)

        notebook.next_page()
        self.assertIsNotNone(preferencesDialog.hint_tab)

        notebook.next_page()
        self.assertIsNotNone(preferencesDialog.theme_tab)

        notebook.next_page()
        self.assertIsNotNone(preferencesDialog.sound_tab)

        notebook.next_page()
        self.assertIsNotNone(preferencesDialog.save_tab)

        widgets["preferences_dialog"].hide()

    async def test5(self):
        """Open engine discoverer dialog"""
        dd = DiscovererDialog(discoverer)

        def on_all_engines_discovered(discoverer, event):
            print("on_all_engines_discovered() OK")
            event.set()

        event = asyncio.Event()
        discoverer.connect("all_engines_discovered", on_all_engines_discovered, event)

        await dd.start()

        await asyncio.wait_for(event.wait(), timeout=5)

        dd.close()

    async def test6(self):
        """Setup dialog emits/loads Chess960 X-FEN file-letter castling"""
        from pychess.Utils.const import (
            FISCHERRANDOMCHESS,
            SETUPCHESS,
            W_OO,
            W_OOO,
            B_OO,
            B_OOO,
        )
        from pychess.Utils.lutils.LBoard import LBoard

        Setup = newGameDialog.SetupPositionExtension
        saved = Setup.castl
        try:
            # Output path (get_fen): a standard FRC start round-trips to file
            # letters through reprCastling() rather than KQkq or "-".
            Setup.castl = {W_OO, W_OOO, B_OO, B_OOO}
            std = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
            self.assertEqual(
                Setup._castling_field(FISCHERRANDOMCHESS, std, "w"), "HAha"
            )

            # Asymmetric Chess960 placement (rooks on b/g files, king on e).
            asym = "nrbnkqbr/pppppppp/8/8/8/8/PPPPPPPP/NRBNKQBR"
            self.assertEqual(
                Setup._castling_field(FISCHERRANDOMCHESS, asym, "w"), "HBhb"
            )

            # Classical chess must still produce canonical KQkq (no regression).
            self.assertEqual(Setup._castling_field(NORMALCHESS, std, "w"), "KQkq")

            # No castling flags -> "-".
            Setup.castl = set()
            self.assertEqual(Setup._castling_field(NORMALCHESS, std, "w"), "-")

            # Load path (ini_widgets): SETUPCHESS parser understands file letters
            # so the checkboxes can be populated from a Chess960 FEN.
            lb = LBoard(SETUPCHESS)
            lb.applyFen("nrbnkqbr/pppppppp/8/8/8/8/PPPPPPPP/NRBNKQBR w BGbg - 0 1")
            self.assertTrue(lb.castling & W_OO)
            self.assertTrue(lb.castling & W_OOO)
            self.assertTrue(lb.castling & B_OO)
            self.assertTrue(lb.castling & B_OOO)
        finally:
            Setup.castl = saved


if __name__ == "__main__":
    unittest.main()
