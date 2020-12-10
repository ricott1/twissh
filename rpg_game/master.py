import time, datetime, os, sys, uuid, random
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import character, world
from rpg_game.utils import quick_data

GAME_SPEED = 1

class Master(object):
    def __init__(self, update_timestep = 0.025):
        self.players = {}
    
        self.redraw = False
        self.time = time.time()
        self.world = world.World()
        
    def quick_game(self, _id):
        data = quick_data()
        self.create_player(_id, data)
        print("PLAYER CREATED", len(self.players))
        
    def create_player(self, _id, data):
        p = character.Player(_id, data, location=self.world.locations[0])
        self.players[_id] = p 
    
    def disconnect(self, _id):
        if _id in self.players:
            del self.players[_id]  
        
    def on_update(self, *args):
        DELTATIME =  time.time() - self.time
        self.time = time.time()
        WORK_MODIFIER = 1
        self.world.on_update()
        for id, p in self.players.items():
            #change to return True if something changed
            p.on_update(GAME_SPEED * DELTATIME * WORK_MODIFIER)
            self.redraw = self.redraw or p.redraw
            p.redraw = False




