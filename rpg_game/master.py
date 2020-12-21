import time, datetime, os, sys, uuid, random
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import character, world
from rpg_game.utils import random_stats, random_name
from rpg_game.constants import GAME_SPEED


class Master(object):
    def __init__(self, update_timestep = 0.025):
        self.players = {}
        self.chat_log = []
        self.redraw = False
        self.time = time.time()
        self.world = world.World()
        
    def on_start(self, _id):
        p = character.Player(_id=_id, _name=random_name(), _stats=random_stats(), _location=self.world.locations[0])
        self.players[p.id] = p 
    
    def disconnect(self, _id):
        print("disconnect", _id)
        if _id in self.players:
            print("deleting", _id)
            #comment next line to keep disconnected bodies in (maybe set them dead)
            self.players[_id].destroy()
            del self.players[_id]
            
    def on_update(self, *args):
        t = time.time()
        DELTATIME =  t - self.time
        self.time = t
        self.redraw = False
        self.world.on_update(GAME_SPEED * DELTATIME)
        self.redraw = self.world.redraw
        sending = [l  for _id, p in self.players.items() for l in p.chat_sent_log]
        
        self.redraw = self.redraw or len(sending) > 0
        for _id, p in self.players.items():
            p_sending = [m for m in sending if m['sender'] != p.name]#bug for same names characters
            p.chat_sent_log = []
            p.chat_received_log += p_sending
                
        
            
