# encoding: utf-8

from sshattrick.game import Game, Side
from sshattrick.master import SSHattrick
from .utils import attr_button, img_to_urwid_text
from typing import Callable
import urwid

from hacknslassh.constants import *
from urwid import raw_display

SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()

MENU_WIDTH = 30
FOOTER_HEIGHT = 4
IMAGE_MAX_HEIGHT = 20


class Scene(object):
    def __init__(self, mind, *args, palette=None, **kwargs):
        # mixin class for frame and scene properties
        self.palette = palette
        super().__init__(*args, **kwargs)
        self.mind = mind
        self.master = self.mind.master
    
    def handle_input(self, _input: str) -> None:
        pass

    def restart(self) -> None:
        pass

    def register_callback(self, event_name: str, callback: Callable, priority: int = 0) -> None:
        self.mind.register_callback(event_name, callback, priority)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        self.mind.process_event(event_name, *args, **kwargs)
        
class TitleFrame(urwid.Frame):
    def __init__(self, _title, _attribute=None, _font=urwid.HalfBlock5x4Font()):
        if _attribute:
            _title = [(_attribute, t) for t in _title]
        bigtext = urwid.Pile([urwid.Padding(urwid.BigText(t, _font), "center", None) for t in _title])
        super().__init__(urwid.Filler(bigtext))

class CreateOrJoinRoom(Scene, urwid.Pile):
    def __init__(self, mind) -> None:
        self.title = urwid.WidgetDisable(TitleFrame(["SSHattrick"]))
        self.name_edit = urwid.Edit("Name: ")
        create_room_btn = attr_button("Create Room", on_press=self.new_game)
        open_games = [urwid.Text(g.name) for g in mind.master.games.values()]
        print("GAMES", open_games)
        _walker = urwid.SimpleListWalker(open_games + [urwid.Columns([self.name_edit, create_room_btn])])
        self.main = urwid.ListBox(_walker)
        super().__init__(mind, [(4, self.title), self.main], focus_item=1)
    
    # def keypress(self, size, key):
    #     key = super().keypress(size, key)
    #     self.emit_event("redraw_local_ui")
    #     return key
    
    def new_game(self, *args):
        name = self.name_edit.get_edit_text()
        self.mind.master.register_new_game(self.mind, name)
        self.emit_event("new_game")


class GameFrame(Scene, urwid.Frame):
    def __init__(self, mind) -> None:
        self.mind = mind
        self.game = None
        self.player = None

        _walker = urwid.SimpleListWalker([urwid.Text("")])
        self.main = urwid.ListBox(_walker)
        super().__init__(mind, urwid.WidgetDisable(self.main))
        self.register_callback("redraw_local_ui_next_cycle", self.update, priority=1)
        self.register_callback("game_joined", self.new_game)
    
    def handle_input(self, _input: str) -> None:
        if self.player:
            self.player.handle_input(_input)
    
    def new_game(self, game: Game, side: Side) -> None:
        print("new game", game, side)
        self.game = game
        self.player = self.game.red_player if side == Side.RED else self.game.blue_player
    
    def update(self) -> None:
        if self.game:
            self.main.body[0].set_text(img_to_urwid_text(self.game.image()))

    