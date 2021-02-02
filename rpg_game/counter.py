from rpg_game.constants import *
import entity

class Counter(object):
    def __init__(self, _name="", _entity=None, _value=0):
        self.name = _name
        self.entity = _entity
        if self.name in self.entity.counters:
            self.entity.counters[self.name].on_end()  
        self.entity.counters[self.name] = self
        self.value = _value
        #if ended, will be removed during entity.on_update 
        self.ended = False
        self.on_set()

    def on_set(self, *args):
        pass

    def on_end(self):
        self.ended = True

    def on_update(self, _deltatime):
        if self.value > 0:
            self.value -= COUNTER_MULTI * _deltatime
            if self.value == 0:
                self.on_end()

    @property
    def value(self):
        return max(0, min(COUNTER_MAX, self._value))  

    @value.setter
    def value(self, val):
        self._value = val

class BuffCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value, _char, _buff_value=0):
        self.char = _char
        self.buff_value = _buff_value
        super().__init__(_name=f"{self.char}_buff", _entity=_entity, _value=_value)

    def on_set(self):
        super().on_set()
        if hasattr(self.entity, self.char):
            c = getattr(self.entity, self.char)
            c.temp_bonus += self.buff_value

    def on_end(self):
        super().on_end()
        if hasattr(self.entity, self.char):
            c = getattr(self.entity, self.char)
            c.temp_bonus -= self.buff_value

class PoisonCounter(Counter):
    """docstring for PoisonCounter"""
    def __init__(self, _entity, _value, _intensity=1):
        super().__init__(_name=f"poison", _entity=_entity, _value=_value)
        self.dmg = 0
        self.intensity = _intensity

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.dmg += self.intensity * _deltatime
        v = int(self.dmg)
        if v:
            self.entity.hit(v)
            self.dmg -= v

class ChargeBuffCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value, _char, _buff_value=0):
        self.char = _char
        self.buff_value = _buff_value
        super().__init__(_name=f"{self.char}_charge_buff", _entity=_entity, _value=_value)

    def on_set(self):
        super().on_set()
        if hasattr(self.entity, self.char):
            c = getattr(self.entity, self.char)
            c.temp_bonus += self.buff_value

    def on_update(self, _deltatime):
        if self.value > 0:
            self.value -= COUNTER_MULTI * _deltatime
            if self.value == 0 or "charge" not in self.entity.counters:
                self.on_end()

    def on_end(self):
        super().on_end()
        if hasattr(self.entity, self.char):
            c = getattr(self.entity, self.char)
            c.temp_bonus -= self.buff_value

class MarkerCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _marker, _value):
        self.marker = _marker
        super().__init__(_name=f"marker", _entity=_entity, _value=_value)

    def on_set(self):
        self.entity.location.redraw = True

class ColorCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _color, _value):
        self.color = _color
        super().__init__(_name=f"color", _entity=_entity, _value=_value)

    def on_set(self):
        self.entity.location.redraw = True

class TextCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _text, _value=MAX_RECOIL):
        super().__init__(_name=f"text", _entity=_entity, _value=_value)
        self.text = _text

    def on_set(self):
        self.entity.location.redraw = True


class HideCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self,  _entity, _value=MAX_RECOIL):
        super().__init__(_name="hide", _entity=_entity, _value=_value)

    def on_set(self):
        super().on_set()
        MarkerCounter(self.entity, {k:[" " for _ in self.entity.positions] for k in ("up", "down", "left", "right")}, self.value)

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.entity.recoil += _deltatime * (1 + SHORT_RECOIL)
        if self.entity.slow_recovery:
            self.on_end()

    def on_end(self):
        super().on_end()
        self.entity.counters["marker"].on_end()

class DeathCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value=DEATH_INTERVAL):
        super().__init__(_name="death", _entity=_entity, _value=_value)

    def on_set(self):
        super().on_set()
        TextCounter(self.entity, f"{self.entity.name} is dead")
        MarkerCounter(self.entity, {k:["X" for _ in self.entity.positions] for k in ("up", "down", "left", "right")}, self.value)

    def on_end(self):
        super().on_end()
        self.entity.destroy()

class PortalCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity):
        super().__init__(_name="portal", _entity=_entity, _value=SHORT_RECOIL)

    def on_update(self, _deltatime):
        portal = self.entity.location.get(self.entity.floor)
        if not isinstance(portal, entity.Portal):
            super().on_update(_deltatime)


class ParryCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value):
        super().__init__(_name="parry", _entity=_entity, _value=_value)

    def on_set(self):
        super().on_set()
        MarkerCounter(self.entity, {k:[v for _ in self.entity.positions] for k, v in zip(("up", "down", "left", "right"), ("◠", "◡", "(", ")"))}, self.value)


    def on_end(self):
        super().on_end()
        self.entity.counters["marker"].on_end()

class ChargeCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value, _dash, _attack):
        super().__init__(_name="charge", _entity=_entity, _value=_value)
        self.dash = _dash
        self.attack = _attack

    def on_set(self):
        super().on_set()
        MarkerCounter(self.entity, {k:[v for _ in self.entity.positions] for k, v in zip(("up", "down", "left", "right"), ("⩓", "⩔", "⪡", "⪢"))}, self.value)
        ChargeBuffCounter(self.entity, self.value, "STR", 4)

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.entity.recoil += _deltatime# * (1 + cls.recoil_cost)
        if self.entity.slow_recovery:
            self.on_end()
        elif self.entity.location.is_empty(self.entity.forward):
            self.dash(self.entity)
        else:
            weapon = self.entity.equipment["main_hand"]#use weapon range
            target = self.entity.location.get(self.entity.forward)

            if hasattr(target, "HP"):
                self.attack(self.entity, target)
            self.on_end()

    def on_end(self):
        super().on_end()
        self.entity.counters["marker"].on_end()

class SingCounter(Counter):
    """docstring for BuffCounter"""
    def __init__(self, _entity, _value, _on_song_hit):
        super().__init__(_name="sing", _entity=_entity, _value=_value)
        self.on_song_hit = _on_song_hit

    def on_update(self, _deltatime):
        super().on_update(_deltatime)
        self.entity.recoil += _deltatime * (1 + MED_RECOIL)
        if self.entity.slow_recovery:
            self.on_end()
        self.spawn_songs()

    def spawn_songs(self):
        x, y, z = self.entity.position
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                pos = (x+dx, y+dy, z+1)
                if self.entity.location.is_empty(pos): 
                    entity.Song(_spawner = self.entity, _on_hit=self.on_song_hit, _location=self.entity.location, _position=pos)
        
