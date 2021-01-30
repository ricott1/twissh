import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import character, world
from rpg_game.utils import random_stats, random_name
from rpg_game.constants import GAME_SPEED


class Master(object):
    def __init__(self):
        self.players = {}
        self.chat_log = []
        self.world = world.World()
        
    def on_start(self, _id):
        pass

    def new_player(self, _id, _class):
        p = character.Player(_id=_id, _name=random_name(), _location=self.world.starting_location(), _game_class = _class)
        self.players[p.id] = p
    
    def disconnect(self, _id):
        print("disconnect", _id)
        if _id in self.players:
            print("deleting", _id)
            #comment next line to keep disconnected bodies in (maybe set them dead)
            #self.players[_id].destroy()
            self.players[_id].kill()
            #del self.players[_id]
            
    def on_update(self, _deltatime):
        
        self.world.on_update(GAME_SPEED * _deltatime)
        
        
        # sending = [l  for _id, p in self.players.items() for l in p.chat_sent_log]
        # self.redraw = self.redraw or len(sending) > 0
        # for _id, p in self.players.items():
        #     p_sending = [m for m in sending if m['sender_id'] != p.id]
        #     p.chat_sent_log = []
        #     p.chat_received_log += p_sending
                
        
            
