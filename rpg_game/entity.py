from rpg_game.constants import *
from rpg_game.utils import new_id
from rpg_game.characteristic import Characteristic
import action

"""
Entity --> has Body, Location
        on_update
        redraw

Character(Entity)

Projectile(Entity)

Item(Entity)
"""

class Entity(object):
    """docstring for Entity"""
    def __init__(self, _name="", _id=None, _location=None, _position=None, _extra_position = [], _weight=0, _marker=".", _description=[], _layer=1):
        self.name = _name
        self.id = _id if _id else new_id()
        #position refers to the "head" position, i.e. the guiding square. 
        self.position = _position
        #extra position is a list of references of extra body parts with respect to the head
        self.extra_position = _extra_position
        if _location:
            if not _position:
                self.position = _location.free_position(_layer, _extra_position)
            self.location = _location
            #self.location.register(self)
        
        self.weight = _weight
        self.base_marker = _marker
        self.redraw = False
        self.description = _description

    @property
    def forward(self):
        if not self.location:
            return None
        return self.location.forward(self.position, self.direction)
    
    @property
    def marker(self):
        return self.base_marker

    def destroy(self):
        """Destroy body"""
        self.location.unregister(self)
        if self.id in self.location.entities:
            del self.location.entities[self.id]

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, _location):
        # if self.location:
        #     self.location.unregister(self)
        self._location = _location
        self.location.register(self)

    def on_update(self, *args):
        pass

class Empty(Entity):
    pass


class Wall(Entity):
    def __init__(self, _HP=100, **kwargs):
        super().__init__(**kwargs)
        self.HP = Characteristic("hit points", "HP", _HP, _min = 0, _max=9999)

class Projectile(Entity):
    """docstring for Projectile"""
    def __init__(self, _movement_speed=2, _max_range=10, _spawner=None, _direction="right", _on_hit=None, **kwargs):
        super().__init__(**kwargs)
        self.spawner = _spawner
        self.movement_speed = _movement_speed
        self.max_range = _max_range
        self.direction = _direction
        self.increment = (0,0,0)
        self.recoil = SHORT_RECOIL
        self.on_hit = _on_hit

    @property
    def recoil(self):
        return self._recoil

    @recoil.setter
    def recoil(self, value):
        self._recoil = min(MAX_RECOIL, max(0, value))

    @property
    def marker(self):
        if self.direction == "up":
            return "↑"
        if self.direction == "down":
            return "↓"
        if self.direction == "left":
            return "←"
        if self.direction == "right":
            return "→"

    def on_update(self, _deltatime):
        s = int(self.recoil)
        if self.recoil > 0:
            self.recoil -= RECOIL_MULTI * _deltatime
            #redraw only if integer changed, hence nneed to display it  
            self.redraw = int(self.recoil) < s

        if self.recoil == 0:
            if self.location.is_empty(self.forward):
                {"right":action.MoveRight, "left":action.MoveLeft, "up":action.MoveUp, "down":action.MoveDown}[self.direction].use(self)
            else:
                if self.on_hit:
                    self.on_hit(self)
                self.destroy()