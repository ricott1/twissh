import time, datetime, os, sys, uuid, random
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import character, world

GAME_SPEED = 1
RANDOM_NAMES = ("Gorbacioff", "Gundam", "Pesca", "Lukiko","Armando","Mariella","Formaggio","Pancrazio","Tancredi","Swallace","Faminy","Pertis","Pericles","Atheno","Mastella","Ciriaco")

class Master(object):
    def __init__(self, update_timestep = 0.025):
        self.players = {}
    
        self.redraw = False
        self.time = time.time()
        self.world = world.World()
        
    def quick_game(self, _id):
        data = quick_data()
        self.create_player(_id, data)
        
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
        self.world.update_visible_maps()
        for id, p in self.players.items():
            #change to return True if something changed
            p.update(GAME_SPEED * DELTATIME * WORK_MODIFIER)
            self.redraw = self.redraw or p.redraw
            p.redraw = False

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def quick_data():
    MP, RES, MAG, SPD, DEX, STR = [sum(sorted([random.randint(1,6) for l in range(4)])[1:]) for x in range(6)]
    HP = 6+ 2* random.randint(0,3)
    HB = 30 + random.randint(1, 30)
    RTM = random.randint(1,2)
    data = {"name" : random.sample(RANDOM_NAMES, 1)[0], "MP" : MP + 6, "HB" : HB, "RES" : RES, "MAG" : MAG, "HP" : HP, "SPD" : SPD, "DEX" : DEX + 6, "STR" : STR + 6, 
    "RTM" : RTM}
    return data
