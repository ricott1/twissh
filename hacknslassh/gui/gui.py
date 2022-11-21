import hacknslassh
from hacknslassh.gui.scenes import CharacterSelectionFrame, NetHackFrame
from hacknslassh.gui.utils import PALETTE
from twissh.server import UrwidMind
import urwid


class GUI(urwid.Frame):
    def __init__(self, mind: UrwidMind):
        self.mind = mind
        self.master: hacknslassh.HackNSlassh = self.mind.master
        self.palette = PALETTE
        self.active_body = CharacterSelectionFrame(self.mind)
        super().__init__(self.active_body)
        self.mind.register_callback("new_player", self.start_game_frame)

    def handle_input(self, _input):
        self.active_body.handle_input(_input)

    def start_game_frame(self):
        self.active_body = NetHackFrame(self.mind)
        self.contents["body"] = (self.active_body, None)