# encoding: utf-8

import os, sys

from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse, AllowAnonymousAccess


#local imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from twisted_serve_ssh import UrwidMind, create_application

from rpg_game.gui import GUI as GameGUI
from rpg_game.gui import PALETTE as GamePalette
from rpg_game.master import Master as GameMaster 

class GameMind(UrwidMind):
    ui_palette = GamePalette
    ui_toplevel = GameGUI
    master = GameMaster()

mind_factories = {
	b"rpg_game" : GameMind
}

cred_checkers = [InMemoryUsernamePasswordDatabaseDontUse(rpg_game=b'')]

application = create_application('TXP', mind_factories, cred_checkers, 6022)

# vim: ft=python

