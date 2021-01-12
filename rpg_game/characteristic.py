from rpg_game.utils import mod
import counter

class Characteristic(object):
    def __init__(self, entity, name, short, value, _min=3, _max=18):
        self.entity = entity
        self.name = name
        self.short = short
        self._value = value
        self._min = _min
        self._max = _max
        self._dmg = 0
        self.temp_bonus = 0
        #setattr(self.entity, self.short.lower(), property(lambda self: self.value))

    @property
    def bonus(self):
        _bonus = self.temp_bonus
        if hasattr(self.entity, "equipment"):
            for k, eqp in self.entity.equipment.items():
                if eqp and self.short in eqp.bonus:
                    _bonus += self.entity.equipment[k].bonus[self.short]
        if hasattr(self.entity, "game_class"):
            if self.short in self.entity.game_class.bonus:
                _bonus += self.entity.game_class.bonus[self.short]
        return _bonus

    @property
    def mod(self):
        return mod(self.value)

    @property
    def dmg(self):
        return self._dmg
    @dmg.setter
    def dmg(self, value):
        self._dmg = max(0, value)
        if self.value <= 0:
            counter.DeathCounter(self.entity)

    @property
    def max(self):
        v = self._value + self.bonus
        return max(self._min, min(self._max, v))

    @property
    def value(self):
        v = self._value + self.bonus - self.dmg
        return max(self._min, min(self._max, v))  



