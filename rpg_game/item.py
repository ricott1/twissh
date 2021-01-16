from rpg_game.utils import new_id
import entity, game_class, counter
     
class Item(entity.Entity):
    def __init__(self, _marker="i", _rarity="common", _in_inventory_marker="i", _extra_inventory_markers= [], _inventory_extra_positions=[], **kwargs):
        super().__init__(_marker=_marker, _layer=0, **kwargs)
        self.type = []
        self.rarity = _rarity #common, uncommon, rare, unique, set
        self.color = self.rarity

        if not isinstance(_in_inventory_marker, list):
            _in_inventory_marker = [_in_inventory_marker]
        if not _extra_inventory_markers:
            _extra_inventory_markers = [_in_inventory_marker for _ in _inventory_extra_positions]
        self.in_inventory_marker = _in_inventory_marker + _extra_inventory_markers
        self.inventory_extra_positions = _inventory_extra_positions
        self.in_inventory_last_positions = list(self.in_inventory_positions)

    @property
    def is_consumable(self):
        return isinstance(self, Consumable)
    @property
    def is_equipment(self):
        return isinstance(self, Equipment)

    @property
    def status(self):
        return [(self.rarity, f"{self.name:12s} {type(self).__name__} {self.rarity}")]

    @property
    def in_inventory_positions(self):
        x, y, z = self.position
        return [(x+xp, y+yp, z+zp) for xp, yp, zp in [(0,0,0)] + self.inventory_extra_positions]
    
    
class Equipment(Item):
    def __init__(self, _marker="e", _bonus={}, **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.eq_description = "Equipment placeholder"
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
        super().__init__(_marker=_marker, _in_inventory_marker="U", **kwargs)#⩌🝅

    def on_use(self, *args):
        self.destroy()

class Potion(Consumable):
    def __init__(self, _effect, **kwargs):
        super().__init__(**kwargs)
        self.effect = _effect

    def on_use(self, user):
        for eff in self.effect:
            getattr(user, eff).dmg -= self.effect[eff]
        counter.TextCounter(user, f"Drink a potion, restored {self.effect}")
        self.destroy()


class Armor(Equipment):
    def __init__(self, _dmg_reduction=0, _marker="a", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["body"]
        self.dmg_reduction = _dmg_reduction
        self.eq_description = f"Reduction {_dmg_reduction}"

class Helm(Equipment):
    def __init__(self, _marker="h", **kwargs):
        super().__init__(_marker=_marker, _in_inventory_marker="/", _extra_inventory_markers= ["\\", "|", "|"], _inventory_extra_positions=[(0,1,0),(1,0,0),(1,1,0)], **kwargs)
        self.type = ["helm"]
        
class Boots(Equipment):
    def __init__(self, _marker="b", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["boots"]
        
class Gloves(Equipment):
    def __init__(self, _marker="g", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["gloves"]

class Belt(Equipment):
    def __init__(self, _marker="l", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["belt"]
    
class Weapon(Equipment):
    def __init__(self, _dmg=(1,6), _marker="w", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["main_hand", "off_hand"]
        self.eq_description = f"Damage:{_dmg[0]}d{_dmg[1]}  " + self.eq_description
        self.dmg = _dmg

class Sword(Weapon):
    def __init__(self, _dmg=(1,6), _marker="w", **kwargs):
        super().__init__(_dmg=_dmg, _marker=_marker, _in_inventory_marker="<", _extra_inventory_markers= ["=", "⫤", "-"], _inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0)], **kwargs)
        self.type = ["main_hand", "off_hand"]
        self.eq_description = f"Melee:{_dmg[0]}d{_dmg[1]}  " + self.eq_description

class Hammer(Weapon):
    def __init__(self, _dmg=(1,6), _marker="w", **kwargs):
        super().__init__(_dmg=_dmg, _marker=_marker, _in_inventory_marker="█", _extra_inventory_markers= ["=", "=", "="], _inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0)], **kwargs)
        self.type = ["main_hand", "off_hand"]
        self.eq_description = f"Melee:{_dmg[0]}d{_dmg[1]}  " + self.eq_description

class Bow(Weapon):
    def __init__(self, _dmg=(1,6), _marker="b", **kwargs):
        super().__init__(_dmg=_dmg, _marker=_marker, **kwargs)
        self.type = ["main_hand"]
        self.eq_description = f"Range:{_dmg[0]}d{_dmg[1]}"

class Shield(Equipment):
    def __init__(self, _marker="s", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = ["off_hand"]
        self.eq_description = f"Action: Parry"

    def requisites(self, user):
        return "parry" in user.game_class.class_actions
 
   

