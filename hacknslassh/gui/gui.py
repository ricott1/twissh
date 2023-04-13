import hacknslassh
from hacknslassh.gui.scenes import CharacterSelectionFrame, NetHackFrame
from hacknslassh.gui.utils import PALETTE
from web.server import UrwidMind
import urwid


class GUI(urwid.Frame):
    def __init__(self, mind: UrwidMind):
        self.mind = mind
        self.master: hacknslassh.HackNSlassh = self.mind.master
        self.palette = PALETTE
        if self.mind.avatar.uuid.bytes in self.master.player_ids:
            self.master.register_new_player(self.mind)
            self.active_body = NetHackFrame(self.mind)
            self.contents["body"] = (self.active_body, None)
        else:
            self.active_body = CharacterSelectionFrame(self.mind)
            self.mind.register_callback("new_player", self.start_game_frame)
        super().__init__(self.active_body)
        
    def handle_input(self, _input: str) -> None:
        self.active_body.handle_input(_input)

    def start_game_frame(self) -> None:
        self.active_body = NetHackFrame(self.mind)
        self.contents["body"] = (self.active_body, None)