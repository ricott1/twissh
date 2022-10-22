# encoding: utf-8

from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

from twissh.server import UrwidMind

if TYPE_CHECKING:
    from mathclassh.master import MathClassH
from ..mathematician import Mathematician
from .frames import DoubleLineBox
from .utils import img_to_urwid_text
from typing import Callable
import urwid

from urwid import raw_display

SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()

MENU_WIDTH = 30
FOOTER_HEIGHT = 4
IMAGE_MAX_HEIGHT = 20


class Scene(object):
    def __init__(self, mind: UrwidMind, *args, palette=None, **kwargs):
        # mixin class for frame and scene properties
        self.palette = palette
        super().__init__(*args, **kwargs)
        self.mind = mind
        self.master: MathClassH = self.mind.master
    
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


class SideView(Scene, urwid.Columns):
    def __init__(self, mind, left, right) -> None:
        self.left = left
        self.right = right
        super().__init__(mind, [urwid.WidgetDisable(urwid.LineBox(self.left)), urwid.LineBox(urwid.WidgetDisable(self.right))])
    
    def handle_input(self, _input: str) -> None:
        self.left.handle_input(_input)
        self.right.handle_input(_input)

class DisplayView(str, Enum):
    DESCRIPTION = 'description'
    STATS = 'stats'

class DisplayMathematician(Scene, urwid.Frame):
    def __init__(self, mind, mathematician: Mathematician) -> None:
        # self.title = urwid.WidgetDisable(TitleFrame(["Math Class H"]))
        self.mathematician = mathematician
        
        # img = ImageCollection.BLUE_FRAME.copy()
        # img.blit(self.mathematician.portrait, (2, 3))
        img_walker = urwid.SimpleListWalker([urwid.Text(img_to_urwid_text(self.mathematician.portrait))])
        portrait = DoubleLineBox(urwid.ListBox(img_walker))

        self.side_text = urwid.Text("\n" + self.mathematician.general_info)
        side = urwid.ListBox(urwid.SimpleListWalker([self.side_text]))
        top = urwid.Columns([(self.mathematician.portrait.get_width() + 2, portrait), side])
        self.middle_text = urwid.Text(self.mathematician.description)
        description = urwid.ListBox(urwid.SimpleListWalker([self.middle_text]))
        self.bottom_text = urwid.Text(" Press 's' to see stats")
        footer = urwid.ListBox(urwid.SimpleListWalker([self.bottom_text]))
        self.body = urwid.Pile([(self.mathematician.portrait.get_height()//2 + 2, top), description, (1, footer)])
        super().__init__(mind, self.body)
        self.view = DisplayView.DESCRIPTION
    
    def handle_input(self, _input: str) -> None:
        if _input == "s":
            if self.view != DisplayView.STATS:
                self.middle_text.set_text(self.mathematician.stats_description)
                self.bottom_text.set_text(" Press 'd' to see description")
                self.view = DisplayView.STATS
        elif _input == "d":   
            if self.view != DisplayView.DESCRIPTION:
                self.middle_text.set_text(self.mathematician.description + self.mathematician.skill_description)
                self.bottom_text.set_text(" Press 's' to see stats")
                self.view = DisplayView.DESCRIPTION

