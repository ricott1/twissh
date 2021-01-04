from rpg_game.constants import *
from rpg_game.utils import new_id, distance
from rpg_game.characteristic import Characteristic
import action
import math, collections

nested_dict = lambda: collections.defaultdict(nested_dict)


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
    def __init__(self, _name="", _id=None, _location=None, _position=(), _extra_position = [], _weight=0, _marker=".", _extra_markers= [], _description=[], _layer=1, _direction="down"):
        self.name = _name
        self.id = _id if _id else new_id()
        self.direction = _direction
        if _location and not _position:
            _position = _location.free_position(_layer, _extra_position)
        self.position = _position
        self.extra_position = _extra_position
        self._location = _location
        self.location = _location

        
        self.weight = _weight
        if not isinstance(_marker, list):
            _marker = [_marker]
        if not _extra_markers:
            _extra_markers = [_marker[0] for _ in _extra_position]
        self._marker = _marker + _extra_markers
        self.redraw = False
        self.description = _description

    @property
    def forward(self):
        x, y, z = self.position
        delta_x = int(self.direction=="down") - int(self.direction=="up")
        delta_y = int(self.direction=="right") - int(self.direction=="left")
        return (x + delta_x, y + delta_y, z)
    # @property
    # def backward(self):
    #     x, y, z = self.position
    #     delta_x = int(user.direction=="down") - int(user.direction=="up")
    #     delta_y = int(user.direction=="right") - int(user.direction=="left")
    #     return (x + delta_x, y + delta_y, z)
    # @property
    # def right_side(self):
    #     x, y, z = self.position
    #     delta_x = int(user.direction=="down") - int(user.direction=="up")
    #     delta_y = int(user.direction=="right") - int(user.direction=="left")
    #     return (x + delta_x, y + delta_y, z)
    # @property
    # def left_side(self):
    #     x, y, z = self.position
    #     delta_x = int(user.direction=="down") - int(user.direction=="up")
    #     delta_y = int(user.direction=="right") - int(user.direction=="left")
    #     return (x + delta_x, y + delta_y, z)
    
    @property
    def marker(self):
        return self._marker

    def destroy(self):
        """Destroy body"""
        if self.location:
            self.location.unregister(self)

    @property
    def positions(self):
        x, y, z = self.position
        #don't transform coordinates
        if self.direction == "down":
            _extra_positions = [(x, y, z) for x, y, z in self.extra_position]
        elif self.direction == "up":
            _extra_positions = [(-x, -y, z) for x, y, z in self.extra_position]
        elif self.direction == "right":
            _extra_positions = [(y, -x, z) for x, y, z in self.extra_position]
        elif self.direction == "left":
            _extra_positions = [(-y, x, z) for x, y, z in self.extra_position]
        return [(x+xp, y+yp, z+zp) for xp, yp, zp in [(0,0,0)] + _extra_positions]
    
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, _location):
        if self._location:
            self._location.unregister(self)
        self._location = _location
        self._location.register(self)

    def on_update(self, *args):
        pass

class Empty(Entity):
    pass


class Wall(Entity):
    def __init__(self, _HP=100, **kwargs):
        super().__init__(**kwargs)
        self.HP = Characteristic(self, "hit points", "HP", _HP, _min = 0, _max=9999)

class Trap(Entity):
    def __init__(self, _HP=100, **kwargs):
        super().__init__(_layer=0, **kwargs)
        

class ActingEntity(Entity):
    def __init__(self, _movement_speed=1, **kwargs):
        super().__init__(**kwargs)
        
        self.movement_speed = _movement_speed
        self.movement_recoil = 0
        self.recoil = 0
        self.slow_recovery = False

        self.actions = {}
        self.action_counters = nested_dict()

    @property
    def recoil(self):
        return self._recoil

    @recoil.setter
    def recoil(self, value):
        self._recoil = min(MAX_RECOIL, max(0, value))
        #if reaches max recoil, slow down recovery
        if self._recoil == MAX_RECOIL:
            self.slow_recovery = True
        #if recovers all recoil, set it back to fast
        elif self._recoil == 0:
            self.slow_recovery = False

    @property
    def movement_recoil(self):
        return self._movement_recoil

    @movement_recoil.setter
    def movement_recoil(self, value):
        self._movement_recoil = min(MAX_RECOIL, max(0, value))
        #if reaches max recoil, slow down recovery
        # if self._movement_recoil == MAX_RECOIL:
        #     self.slow_recovery = True
        # #if recovers all recoil, set it back to fast
        # elif self._movement_recoil == 0:
        #     self.slow_recovery = False

    def on_update(self, _deltatime):
        s = math.ceil(REDRAW_MULTI*self.recoil)
        if self.recoil > 0:
            #if slow recovery, only recover portion of it
            self.recoil -= RECOIL_MULTI * _deltatime * (1 - SLOW_RECOVERY_MULTI*int(self.slow_recovery))
            #redraw only if integer changed, hence nneed to display it  
            self.redraw = math.ceil(REDRAW_MULTI*self.recoil) != s
        if self.movement_recoil > 0:
            #if slow recovery, only recover portion of it
            self.movement_recoil -= RECOIL_MULTI * _deltatime * (1 - SLOW_RECOVERY_MULTI*int(self.slow_recovery))

        for key in self.actions:
            self.actions[key].on_update(self, _deltatime)
            if self.action_counters[key] > 0:
                self.action_counters[key] -= COUNTER_MULTI * _deltatime
                if self.action_counters[key] <= 0:
                    #self.actions[key].on_end()
                    self.action_counters[key] = 0
                    self.redraw = True

class Projectile(ActingEntity):
    """docstring for Projectile"""
    def __init__(self, _movement_speed=5, _max_range=10, _spawner=None, _direction="right", _on_hit=lambda : None, **kwargs):
        super().__init__(_movement_speed=_movement_speed, _direction=_direction, **kwargs)
        self.spawner = _spawner
        self.spawn_position = tuple(self.position)
        self.max_range = _max_range
        self.is_dead = False
        self.recoil = 0
        self.movement_recoil = 0
        self.on_hit = _on_hit

    @property
    def marker(self):
        return [{"up":"↑", "down":"↓", "left":"←", "right":"→"}[self.direction] for _ in self.positions]

    def on_update(self, _deltatime):
        if distance(self.position, self.spawn_position) > self.max_range:
            self.destroy()
            return

        super().on_update(_deltatime)

        if self.location.is_empty(self.forward):
            {"right":action.DashRight, "left":action.DashLeft, "up":action.DashUp, "down":action.DashDown}[self.direction].use(self)
        elif self.movement_recoil == 0:
            self.on_hit(self)
            self.destroy()

class Arrow(Projectile):
    def __init__(self, _spawner, _on_hit, **kwargs):
        super().__init__(_spawner=_spawner, _on_hit=_on_hit, _movement_speed=6, _direction=_spawner.direction, _position=_spawner.forward, _location=_spawner.location, **kwargs)
        self.movement_recoil = SHORT_RECOIL * (1 - MOD_WEIGHT * _spawner.DEX.mod)
        self.max_range = 8 + _spawner.DEX.mod
        self.movement_speed = 5 + 0.5 * _spawner.DEX.mod

class FireBall(Projectile):
    def __init__(self, _spawner, _on_hit, _direction, _position, _fragment, _location=None, **kwargs):
        if not _location:
            _location = _spawner.location
        super().__init__(_spawner=_spawner, _on_hit=_on_hit, _movement_speed=4, _direction=_direction, _position=_position, _location=_location, **kwargs)
        self.movement_recoil = SHORTER_RECOIL * (1 - MOD_WEIGHT * _spawner.INT.mod)
        self.max_range = 6 + _spawner.INT.mod
        self.movement_speed = 1.5 + 0.25 * _spawner.INT.mod
        self.fragment = _fragment

    def on_update(self, _deltatime):
        if distance(self.position, self.spawn_position)> self.max_range:
            self.on_hit(self)
            self.destroy()
            return
        super().on_update(_deltatime)

    @property
    def marker(self):
        if self.fragment > 1:
            return [("red", "◉")]
        return [("red", "◎")]

