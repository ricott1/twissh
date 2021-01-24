from rpg_game.utils import new_id
import entity, game_class, counter, location
     
class Item(entity.Entity):
    def __init__(self, _marker="i", _rarity="common", _encumbrance=1, _in_inventory_marker="i", _extra_inventory_markers= [], _in_inventory_extra_positions=[], **kwargs):
        super().__init__(_marker=_marker, _layer=0, **kwargs)
        self.type = None
        self.rarity = _rarity #common, uncommon, rare, unique, set
        self._color = self.rarity
        self.encumbrance = _encumbrance

        if not isinstance(_in_inventory_marker, list):
            _in_inventory_marker = [_in_inventory_marker]
        if not _extra_inventory_markers:
            _extra_inventory_markers = [_in_inventory_marker for _ in _in_inventory_extra_positions]
        self.in_inventory_marker = _in_inventory_marker + _extra_inventory_markers
        self.in_inventory_extra_positions = _in_inventory_extra_positions

    @property
    def is_consumable(self):
        return isinstance(self, Consumable)
    @property
    def is_equipment(self):
        return isinstance(self, Equipment)

    @property
    def status(self):
        return [(self.rarity, f"{self.name:16s}: {type(self).__name__} {self.description}")]

    @property
    def positions(self):
        x, y, z = self.position
        # if isinstance(self.location, location.Inventory):
        #     _extra_positions = self.in_inventory_extra_positions
        # else:
        _extra_positions = self.extra_positions

        #don't transform coordinates if facing down.
        if self.direction == "down":
            _extra_positions = [(x, y, z) for x, y, z in _extra_positions]
        elif self.direction == "up":
            _extra_positions = [(-x, -y, z) for x, y, z in _extra_positions]
        elif self.direction == "right":
            _extra_positions = [(-y, x, z) for x, y, z in _extra_positions]
        elif self.direction == "left":
            _extra_positions = [(y, -x, z) for x, y, z in _extra_positions]
        return [(x+xp, y+yp, z+zp) for xp, yp, zp in [(0,0,0)] + _extra_positions]

    @property
    def marker(self):
        return self.direction_markers[self.direction]
    
    
class Equipment(Item):
    def __init__(self, _marker="e", _bonus={}, **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.eq_description = ""
        self.bonus = _bonus
        for k, b in self.bonus.items():
            self.eq_description += f"{k}:{b}  "
        self.is_equipped = False

    @property
    def status(self):
        return [(self.rarity, f"{self.name:16s}: {type(self).__name__} {self.eq_description}")]

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
        self.cons_description = ""

    def on_use(self, *args):
        self.destroy()

class Potion(Consumable):
    def __init__(self, _effect, **kwargs):
        super().__init__(_marker="U", **kwargs)
        self.effect = _effect
        self.cons_description = f"{self.effect}"

    def on_use(self, user):
        for eff in self.effect:
            getattr(user, eff).dmg -= self.effect[eff]
        counter.TextCounter(user, f"Drink a potion, restored {self.effect}")
        self.destroy()


class Armor(Equipment):
    def __init__(self, _dmg_reduction=0, _marker="⌂", _encumbrance=4, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _in_inventory_marker="◾", _extra_inventory_markers= ["◡", "◡", "◾","║","◜","◝","║"], _in_inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0),(1,0,0),(1,1,0),(1,2,0),(1,3,0)], **kwargs)
        '''
        ◜◝
        ᒋᒉ
       ◾◡◡◾
       ║◜◝║
       ☰◎☰
       ║║║║
       ,  ,
       ᑯ  ᑲ
        '''
        self.type = "body"
        self.dmg_reduction = _dmg_reduction
        self.eq_description = f"Reduction {_dmg_reduction}"

    def requisites(self, user):
        return user.game_class.name not in ("wizard",)

class Helm(Equipment):
    def __init__(self, _marker="⌓", _encumbrance=2, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _in_inventory_marker="◜", _extra_inventory_markers= ["◝", "ᒋ", "ᒉ"], _in_inventory_extra_positions=[(0,1,0),(1,0,0),(1,1,0)], **kwargs)
        '''
       ◜◝
       ᒋᒉ
        '''
        self.type = "helm"
        
class Boots(Equipment):
    def __init__(self, _marker="b", _encumbrance=2, **kwargs):
        '''
        ,,
        ᑯᑲ

        '''
        super().__init__(_marker=_marker, _encumbrance=2, _in_inventory_marker=",", _extra_inventory_markers= [",", "ᑯ", "ᑲ"], _in_inventory_extra_positions=[(0,1,0),(1,0,0),(1,1,0)], **kwargs)
        self.type = "boots"       
        
class Ring(Equipment):
    def __init__(self, _marker="O", _encumbrance=1, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _in_inventory_marker="O", **kwargs)
        self.type = "ring" 
        
# class Gloves(Equipment):
#     def __init__(self, _marker="g", **kwargs):
#         '''
#         }▬{
#         '''
#         super().__init__(_marker=_marker, _in_inventory_marker="}", _extra_inventory_markers= ["▬", "{"], _in_inventory_extra_positions=[(0,1,0),(0,2,0)], **kwargs)
#         self.type = "gloves"

class Belt(Equipment):
    def __init__(self, _marker="⑄", _encumbrance=2, **kwargs):
        '''
        ☰◎☰
        '''
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _in_inventory_marker="☰", _extra_inventory_markers= ["◎", "☰"], _in_inventory_extra_positions=[(0,1,0),(0,2,0)], **kwargs)
        self.type = "belt"
    
class Weapon(Equipment):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=1, _marker="x", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.type = "main_hand"
        self.eq_description = f"Damage:{_dmg[0]}d{_dmg[1]}  " + self.eq_description
        self.dmg = _dmg
        self.range = _range
        self.critical = _critical
        self.speed = _speed

class Sword(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(19, 2), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_marker="<", _extra_inventory_markers= ["=", "⫤", "-"], _in_inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0)], **kwargs)
        '''
        <==⫤-
        '''
        self.type = "main_hand"
        self.eq_description = f"Melee:{_dmg[0]}d{_dmg[1]}  "

class Hammer(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _speed=1.5, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_marker="█", _extra_inventory_markers= ["=", "=", "="], _in_inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0)], **kwargs)
        '''
        █▰▰▰▰
        '''
        self.type = "two_hands"
        self.eq_description = f"Melee:{_dmg[0]}d{_dmg[1]}  "

class Axe(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 3), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_marker="⌂", _extra_inventory_markers= ["═", "=", "="], _in_inventory_extra_positions=[(0,1,0),(0,2,0),(0,3,0)], **kwargs)
        '''
        ⌂⊨▰▰▰
        '''
        self.type = "two_hands"
        self.eq_description = f"Melee:{_dmg[0]}d{_dmg[1]}  "

class Bow(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=6, _marker="→", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_marker=" ", _extra_inventory_markers= ["/", "(", "|"," ","\\"], _in_inventory_extra_positions=[(0,1,0),(1,0,0),(1,1,0),(2,0,0),(2,1,0)], **kwargs)
        '''
         / 
        (|
         \ 
        '''
        self.type = "two_hands"
        self.eq_description = f"Range {self.range}:{_dmg[0]}d{_dmg[1]}"
        
class Shield(Equipment):
    def __init__(self, _marker="Ø", _encumbrance=3, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _in_inventory_marker="□", _extra_inventory_markers= ["□", "◹", "◸"], _in_inventory_extra_positions=[(0,1,0),(1,0,0),(1,1,0)], **kwargs)
        '''
        ■□
        ◹◤
        ⩌⨷⨁
        '''
        self.type = "off_hand"
        self.eq_description = f"Action: Parry"

    def requisites(self, user):
        return "parry" in user.game_class.class_actions
 

   

