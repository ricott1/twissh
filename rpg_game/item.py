from rpg_game.utils import new_id
import entity
     
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
        return (self.rarity, super().marker)
    
class Equipment(Item):
    def __init__(self, _marker="e", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.eq_description = ""
        self.bonus = {}
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
    def __init__(self, _bonus={}, _dmg_reduction=0, _marker="a", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["body"]
        self.dmg_reduction = _dmg_reduction
        self.eq_description = f"Reduction {_dmg_reduction}"
        self.bonus.update(_bonus)

class Helm(Equipment):
    def __init__(self, _bonus={}, _marker="h", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["helm"]
        self.description = description
        self.bonus.update(_bonus)
        
class Boots(Equipment):
    def __init__(self, _bonus={}, _marker="b", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["boots"]
        self.description = description
        self.bonus.update(_bonus)    
        
class Gloves(Equipment):
    def __init__(self, _bonus={}, _marker="g", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["gloves"]
        self.description = description
        self.bonus.update(_bonus)  

class Belt(Equipment):
    def __init__(self, _bonus={}, _marker="l", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["belt"]
        self.description = description
        self.bonus.update(_bonus) 
    
class Weapon(Equipment):
    def __init__(self, _bonus={}, _dmg=(1,4), _marker="w", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["main_hand", "off_hand"]
        self.eq_description = f"Damage {_dmg[0]}d{_dmg[1]}"
        self.dmg = _dmg
 
   

