from rpg_game.utils import new_id
import entity, game_class
     
class Item(entity.Entity):
    def __init__(self, _marker="i", **kwargs):
        super().__init__(_marker=_marker, _layer=0, **kwargs)
        self.type = None
        self.rarity = "common" #common, uncommon, rare, unique, set

    @property
    def is_consumable(self):
        return isinstance(self, Consumable)
    @property
    def is_equipment(self):
        return isinstance(self, Equipment)

    @property
    def marker(self):
        return [(self.rarity, m) for m in super().marker]
    
class Equipment(Item):
    def __init__(self, _marker="e", _bonus={}, **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.eq_description = ""
        self.bonus = _bonus
        for k, b in self.bonus.items():
            self.eq_description += f"{k}:{b}  "
        self.is_equipped = False

    def on_equip(self, *args):
        self.is_equipped = True

    def on_unequip(self, *args): 
        self.is_equipped = False

    def on_update(self, *args):
        pass   

    def requisites(self, *args):
        return True

class Consumable(Item):
    def __init__(self, _marker="c", **kwargs):
        super().__init__(_marker=_marker, **kwargs)

    def on_use(self, *args):
        pass

class Armor(Equipment):
    def __init__(self, _dmg_reduction=0, _marker="a", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["body"]
        self.dmg_reduction = _dmg_reduction
        self.eq_description = f"Reduction {_dmg_reduction}"

class Helm(Equipment):
    def __init__(self, _marker="h", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["helm"]
        self.description = description
        
class Boots(Equipment):
    def __init__(self, _marker="b", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["boots"]
        self.description = description
        
class Gloves(Equipment):
    def __init__(self, _marker="g", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["gloves"]
        self.description = description

class Belt(Equipment):
    def __init__(self, _marker="l", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["belt"]
        self.description = description
    
class Weapon(Equipment):
    def __init__(self, _dmg=(1,4), _marker="w", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["main_hand", "off_hand"]
        self.eq_description = f"Damage:{_dmg[0]}d{_dmg[1]}  " + self.eq_description
        self.dmg = _dmg

class Bow(Weapon):
    def __init__(self, _dmg=(1,6), _marker="b", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["main_hand"]
        self.eq_description = f"Action: Arrow"
        self.dmg = _dmg

class Shield(Equipment):
    def __init__(self, _marker="s", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["off_hand"]
        self.eq_description = f"Action: Parry"

    def requisites(self, user):
        return isinstance(user.game_class, game_class.Warrior)
 
   

