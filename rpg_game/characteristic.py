from rpg_game.utils import mod

class Characteristic(object):
    def __init__(self, name, short, value, _min=3, _max=25):
        self.name = name
        self.short = short
        self._value = value
        self.bonus = {}
        self._min = _min
        self._max = _max
        self._dmg = 0

    @property
    def mod(self):
        return mod(self.value)

    @property
    def dmg(self):
        return self._dmg
    @dmg.setter
    def dmg(self, value):
        self._dmg = value

    @property
    def max(self):
        bonus = sum([b for k, b in self.bonus.items()])
        v = self._value + bonus
        return max(self._min, min(self._max, v))

    @property
    def value(self):
        bonus = sum([b for k, b in self.bonus.items()])
        v = self._value + bonus - self._dmg
        return max(self._min, min(self._max, v))  
    @value.setter
    def value(self, value):
        v = int(round(value))
        self._value = max(self._min, min(self._max, v))        