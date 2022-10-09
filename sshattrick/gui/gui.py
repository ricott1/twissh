from .scenes import GameFrame, CreateOrJoinRoom
from .utils import PALETTE
import urwid


class GUI(urwid.Frame):
    def __init__(self, mind):
        self.mind = mind
        self.palette = PALETTE
        self.active_body = CreateOrJoinRoom(self.mind)
        super().__init__(self.active_body)
        self.game_frame = GameFrame(self.mind)
        self.mind.register_callback("new_game", self.start_game_frame)

    def handle_input(self, _input):
        self.active_body.handle_input(_input)

    def start_game_frame(self):
        self.active_body = self.game_frame
        self.contents["body"] = (self.active_body, None)