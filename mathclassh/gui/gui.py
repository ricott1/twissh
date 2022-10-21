from __future__ import annotations
import random
from typing import TYPE_CHECKING

from twissh.server import UrwidMind

if TYPE_CHECKING:
    from mathclassh.master import MathClassH
from .scenes import DisplayMathematician, SideView
from .utils import PALETTE
import urwid


class GUI(urwid.Frame):
    def __init__(self, mind: UrwidMind):
        self.mind = mind
        self.master: MathClassH = self.mind.master
        self.palette = PALETTE
        research_group = self.master.register_new_game(mind)

        print(len(research_group.members_list))
        left_math, right_math = random.sample(research_group.members_list, 2)
        left = DisplayMathematician(self.mind, left_math)

        right = DisplayMathematician(self.mind, right_math)
        self.active_body = SideView(self.mind, left, right)
        super().__init__(self.active_body)
        

    def handle_input(self, _input):
        self.active_body.handle_input(_input)
