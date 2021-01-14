from rpg_game.constants import *
from rpg_game.utils import new_id, distance
import characteristic, character, action, counter
import math, random

class Entity(object):
    """docstring for Entity"""
    def __init__(self, _name="", _id=None, _location=None, _position=(), _extra_position = [], _HP=1, _color="white", _marker=".", _extra_markers= [], _description="", _layer=1, _direction="down"):
        self.name = _name
        self.id = _id if _id else new_id()
        self.color = _color
        if not isinstance(_marker, list):
            _marker = [_marker]
        if not _extra_markers:
            _extra_markers = [_marker[0] for _ in _extra_position]
        self._marker = _marker + _extra_markers
        self.direction_markers = {"up":self._marker, "down":self._marker, "left":self._marker, "right":self._marker}

        self._direction = _direction
        self.counters = {}
        if _location and not _position:
            _position = _location.free_position(_layer, _extra_position)
        self._position = _position
        self.extra_position = _extra_position
        self.last_positions = list(self.positions)
        self._location = None
        self.location = _location

        self.HP = characteristic.Characteristic(self, "hit points", "HP", _HP, _min = 0, _max=9999)

        self.description = _description


    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        if self._position == value:
            return
        self.last_positions = list(self.positions)
        self._position = value
        self.location.update_content(self)
    @property
    def positions(self):
        x, y, z = self.position
        #don't transform coordinates if facing down.
        if self.direction == "down":
            _extra_positions = [(x, y, z) for x, y, z in self.extra_position]
        elif self.direction == "up":
            _extra_positions = [(-x, -y, z) for x, y, z in self.extra_position]
        elif self.direction == "right":
            _extra_positions = [(-y, x, z) for x, y, z in self.extra_position]
        elif self.direction == "left":
            _extra_positions = [(y, -x, z) for x, y, z in self.extra_position]
        return [(x+xp, y+yp, z+zp) for xp, yp, zp in [(0,0,0)] + _extra_positions]

    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self, value):
        if self._direction == value:
            return
        self._direction = value
        self.location.redraw = True

    @property
    def forward(self):
        x, y, z = self.position
        delta_x = int(self.direction=="down") - int(self.direction=="up")
        delta_y = int(self.direction=="right") - int(self.direction=="left")
        return (x + delta_x, y + delta_y, z)
    @property
    def above(self):
        x, y, z = self.position
        return (x, y, z+1)
    @property
    def below(self):
        x, y, z = self.position
        return (x, y, z-1)
    @property
    def floor(self):
        x, y, z = self.position
        return (x, y, 0)
    @property
    def back(self):
        x, y, z = self.position
        delta_x = int(user.direction=="down") - int(user.direction=="up")
        delta_y = int(user.direction=="right") - int(user.direction=="left")
        return (x - delta_x, y - delta_y, z)
    @property
    def right_side(self):
        x, y, z = self.position
        delta_x = int(user.direction=="down") - int(user.direction=="up")
        delta_y = int(user.direction=="right") - int(user.direction=="left")
        return (x - delta_y, y - delta_x, z)
    @property
    def left_side(self):
        x, y, z = self.position
        delta_x = int(user.direction=="down") - int(user.direction=="up")
        delta_y = int(user.direction=="right") - int(user.direction=="left")
        return (x + delta_y, y + delta_x, z)
    
    @property
    def marker(self):
        if "marker" in self.counters:
            return self.counters["marker"].marker[self.direction]
        else:
            return self.direction_markers[self.direction]

    @property
    def status(self):
        _status = [("top", f"{self.name:12s} {type(self).__name__}")]
        return _status
    
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, _location):
        if self._location == _location:
            return
        if self._location:
            self._location.unregister(self)
        self._location = _location
        self._location.register(self)

    @property
    def is_dead(self):
        return "death" in self.counters

    def destroy(self):
        """Destroy body"""
        if self.location:
            self.location.unregister(self)

    def on_update(self, _deltatime):
        for key, count in self.counters.copy().items():
            self.counters[key].on_update(_deltatime)
            if self.counters[key].ended:
                del self.counters[key]

    def hit(self, dmg):
        self.HP.dmg += max(0, dmg)
        if self.is_dead:
            self.destroy()

class Empty(Entity):
    pass

class Portal(Entity):
    def __init__(self, **kwargs):
        super().__init__(_name="portal", **kwargs)
        self.partner = None

    @property
    def status(self):
        if self.partner:
            return [("top", f"Portal to {self.partner.location.name}")]
        return [("top", f"Broken portal")]

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        target = self.location.get(self.above)
        if isinstance(target, character.Character):
            self.teleport(target)

    def teleport(self, target):
        if self.partner and "portal" not in target.counters and self.partner.location.is_empty(self.partner.above):
            target.position = self.partner.above
            target.location = self.partner.location
            counter.PortalCounter(target)  


class Wall(Entity):
    def __init__(self, _HP, **kwargs):
        super().__init__(_name="wall", _extra_position=[(0,0,1), (0,0,2)], _HP=_HP, **kwargs)

class HardWall(Wall):
    def __init__(self, _HP=math.inf, **kwargs):
        super().__init__(_HP=_HP, **kwargs)

    @property
    def status(self):
        return None
    

class ThinWall(Wall):
    def __init__(self, _HP=30, **kwargs):
        super().__init__(_HP=_HP, **kwargs)

    @property
    def status(self):
        if self.HP.value < self.HP.max: 
            h = u"─"
        elif self.HP.value == self.HP.max: 
            h = u"┈"
        _status = [("top", f"Wall {h}{self.HP.value}")]
        return _status

    # @property
    # def marker(self):
    #     if self.HP.value > 50:
    #         return [("cyan", "▓")]
    #     elif self.HP.value > 20:
    #         return [("cyan", "▒")]
    #     else:
    #         return [("cyan", "░")]

            # "┄""┈"┆┊

class IceWall(Wall):
    VANISH_COEFF = 1.5
    VANISH_SPAWNER_COEFF = 0.15

    def __init__(self, _spawner=None, **kwargs):
        self.spawner = _spawner
        _HP = 10 * (3 + self.spawner.INT.mod)
        super().__init__(_name="ice wall", _HP=_HP, **kwargs)
        self.color = "cyan"
        self.vanish = 0
        self.vanish_coeff = self.VANISH_COEFF * (1 - self.VANISH_SPAWNER_COEFF * self.spawner.INT.mod)

    @property
    def marker(self):
        if self.HP.value > 50:
            return ["▓"]
        elif self.HP.value > 20:
            return ["▒"]
        else:
            return ["░"]

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        if self.is_dead:
            self.destroy()
        self.vanish += self.vanish_coeff * _deltatime
        v = int(self.vanish)
        self.HP.dmg += v
        self.vanish -= v
    

class Trap(Entity):
    DETECTION_COEFF = 0.25
    DURABILITY_COEFF = 5
    DURABILITY_SPAWNER_COEFF = 0.1
    FINAL_DETECTION = 0.95

    def __init__(self, _spawner=None, _on_hit=lambda : None, **kwargs):
        super().__init__(_layer=0, _marker="⋆", **kwargs)
        self.spawner = _spawner
        self.spawn_position = tuple(self.position)
        self.on_hit = _on_hit
        self.detection_interval = 1.5 - self.DETECTION_COEFF * self.spawner.INT.mod
        self.vanish = 0
        self.durability = self.DURABILITY_COEFF * (1 - self.DURABILITY_SPAWNER_COEFF * self.spawner.INT.mod)
    
    @property
    def marker(self):
        if self.vanish > self.FINAL_DETECTION * self.durability:
            self.color = "red"
            return ["⋆"]
        elif self.vanish < self.detection_interval:
            self.color = "white"
            return ["⋆"]
        return [" "]

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        target = self.location.get(self.above)
        if isinstance(target, character.Character) and target is not self.spawner:
            self.on_hit(self)
            self.destroy()
            return
        self.vanish += _deltatime
        if self.vanish > self.durability:
            self.destroy()

class Song(Entity):
    DURABILITY_COEFF = 8
    DURABILITY_SPAWNER_COEFF = 0.1

    def __init__(self, _spawner=None, _on_hit=lambda : None, **kwargs):
        super().__init__(_layer=0, _marker="⋆", **kwargs)
        self.spawner = _spawner
        self.spawn_position = tuple(self.position)
        self.on_hit = _on_hit
        self.vanish = 0
        self.durability = self.DURABILITY_COEFF * (1 - self.DURABILITY_SPAWNER_COEFF * self.spawner.CHA.mod)
    
    @property
    def marker(self):
        if self.vanish > 0.75 * self.durability:
            return ["♬"]
        elif self.vanish > 0.5 * self.durability:
            return ["♫"]
        elif self.vanish > 0.25 * self.durability:
            return ["♪"]
        return ["♩"]

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        target = self.location.get(self.below)
        if isinstance(target, character.Player) and target is not self.spawner:
            self.on_hit(self)
            self.destroy()
        self.vanish += _deltatime
        if self.vanish > self.durability:
            self.destroy()
    

class ActingEntity(Entity):
    def __init__(self, _movement_speed=1, **kwargs):
        super().__init__(**kwargs)
        
        self.movement_speed = _movement_speed
        self.movement_recoil = 0
        self.recoil = 0
        self.slow_recovery = False
        self.actions = {}

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

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        if self.is_dead:
            return
        s = math.ceil(REDRAW_MULTI*self.recoil)
        if self.recoil > 0:
            #if slow recovery, only recover portion of it
            self.recoil -= RECOIL_MULTI * _deltatime * (1 - SLOW_RECOVERY_MULTI*int(self.slow_recovery))
            #redraw only if integer changed, hence nneed to display it  
            self.location.redraw = math.ceil(REDRAW_MULTI*self.recoil) != s
        if self.movement_recoil > 0:
            #if slow recovery, only recover portion of it
            self.movement_recoil -= RECOIL_MULTI * _deltatime * (1 - SLOW_RECOVERY_MULTI*int(self.slow_recovery))


class Projectile(ActingEntity):
    """docstring for Projectile"""
    def __init__(self, _movement_speed=5, _max_range=10, _spawner=None, _direction="right", _on_hit=lambda : None, **kwargs):
        super().__init__(_movement_speed=_movement_speed, _direction=_direction, **kwargs)
        self.direction_markers = {"up":["↑"], "down":["↓"], "left":["←"], "right":["→"]}
        self.spawner = _spawner
        self.spawn_position = tuple(self.position)
        self.max_range = _max_range
        self.recoil = 0
        self.movement_recoil = 0
        self.on_hit = _on_hit

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
        self.color = "red"
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
            return ["◉"]
        return ["◎"]

