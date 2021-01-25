from rpg_game.utils import new_id
import entity, game_class, counter, location
     
class Item(entity.Entity):
    def __init__(self, _marker="i", _rarity="common", _encumbrance=1, _in_inventory_markers=[], _in_inventory_marker_positions=[], **kwargs):
        super().__init__(_marker=_marker, _layer=0, **kwargs)
        self.type = None
        self.rarity = _rarity #common, uncommon, rare, unique, set
        self._color = self.rarity
        self.encumbrance = _encumbrance

        self.in_inventory_markers = _in_inventory_markers
        self.in_inventory_marker_positions = _in_inventory_marker_positions

    @property
    def is_consumable(self):
        return isinstance(self, Consumable)
    @property
    def is_equipment(self):
        return isinstance(self, Equipment)

    @property
    def status(self):
        return [(self.rarity, f"{self.name}"),f": {type(self).__name__} {self.description}"]

    @property
    def marker(self):
        return self.direction_markers[self.direction]
    
    
class Equipment(Item):
    def __init__(self, _marker="e", _bonus={}, _type=None, **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.bonus = _bonus
        self.is_equipped = False
        self.type = _type
        _type_name = self.type.replace("_", " ")
        _type_name = _type_name[0].upper() + _type_name[1:]
        self.eq_description = f"{_type_name}\n{self.bonus}"
        self.set = {"name":None, "size":0}
        self.set_bonus = {}

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
        super().__init__(_marker=_marker, _in_inventory_markers=["U"], _in_inventory_marker_positions=[(0, 0)],**kwargs)#⩌🝅
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
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _type="body", _in_inventory_markers=["▟","◡", "◡", "▙","║","◜","◝","║"], _in_inventory_marker_positions=[(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3)], **kwargs)
        '''
        ◜◝
        ᒋᒉ
       ▟◡◡▙
       ║◜◝║
       ☰◎☰
       ║║║║
       ,  ,
       ᑯ  ᑲ
        '''
        self.bonus["dmg_reduction"] = _dmg_reduction
        self.eq_description = f"Reduction {_dmg_reduction}"

    def requisites(self, user):
        return user.game_class.name not in ("wizard",)

class Helm(Equipment):
    def __init__(self, _marker="⌓", _encumbrance=2, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _type="helm", _in_inventory_markers=["◜","◝", "ᒋ", "ᒉ"], _in_inventory_marker_positions=[(0,0),(0,1),(1,0),(1,1)], **kwargs)
        '''
       ◜◝
       ᒋᒉ
        '''

        
class Boots(Equipment):
    def __init__(self, _marker="b", _encumbrance=2, **kwargs):
        '''
        ,,
        ᑯᑲ

        '''
        super().__init__(_marker=_marker, _encumbrance=2, _type="boots", _in_inventory_markers=[",",",", "ᑯ", "ᑲ"], _in_inventory_marker_positions=[(0,0),(0,1),(1,0),(1,1)], **kwargs)

        
class Ring(Equipment):
    def __init__(self, _marker="O", _encumbrance=1, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _type="ring", _in_inventory_markers=["O"], _in_inventory_marker_positions=[(0,0)], **kwargs)

        
# class Gloves(Equipment):
#     def __init__(self, _marker="g", **kwargs):
#         '''
#         }▬{
#         '''
#         super().__init__(_marker=_marker, _in_inventory_markers=["}","▬", "{"], _in_inventory_marker_positions=[(0,1),(0,2)], **kwargs)
#         self.type = "gloves"

class Belt(Equipment):
    def __init__(self, _marker="⑄", _encumbrance=2, **kwargs):
        '''
        ☰◎☰
        '''
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _type = "belt", _in_inventory_markers=["☰","◎", "☰"], _in_inventory_marker_positions=[(0,0),(0,1),(0,2)], **kwargs)

    
class Weapon(Equipment):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=1, _marker="x", **kwargs):
        super().__init__(_marker=_marker, **kwargs)
        self.dmg = _dmg
        self.range = _range
        self.critical = _critical
        self.speed = _speed
        _type_name = self.type.replace("_", " ")
        _type_name = _type_name[0].upper() + _type_name[1:]
        self.eq_description = f"Dmg:{_dmg[0]}d{_dmg[1]} Crt:{self.critical}\nRange:{self.range} Speed:{self.speed}\n{_type_name}\n{self.bonus}"
        

class Sword(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(19, 2), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _type="main_hand", _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_markers=["<","=", "⫤", "-"], _in_inventory_marker_positions=[(0,0),(0,1),(0,2),(0,3)], **kwargs)
        '''
        <==⫤-
        '''

class Hammer(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _type="two_hands", _speed=1.5, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_markers=["█","=", "=", "="], _in_inventory_marker_positions=[(0,0),(0,1),(0,2),(0,3)], **kwargs)
        '''
        █▰▰▰▰
        '''

class Axe(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 3), _range=1, _marker="x", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _type="two_hands", _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_markers=["⌂","═", "=", "="], _in_inventory_marker_positions=[(0,0),(0,1),(0,2),(0,3)], **kwargs)
        '''
        ⌂⊨▰▰▰
        '''

class Bow(Weapon):
    def __init__(self, _dmg=(1,6), _speed=1, _critical=(20, 2), _range=6, _marker="→", _encumbrance=3, **kwargs):
        super().__init__(_dmg=_dmg, _encumbrance=_encumbrance, _type="two_hands", _speed=_speed, _critical=_critical, _range=_range, _marker=_marker, _in_inventory_markers=[" ","/", "(", "|"," ","\\"], _in_inventory_marker_positions=[(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)], **kwargs)
        '''
         / 
        (|
         \ 
        '''
        self.eq_description = f"Range {self.range}:{_dmg[0]}d{_dmg[1]}"
        
class Shield(Equipment):
    def __init__(self, _marker="Ø", _encumbrance=3, **kwargs):
        super().__init__(_marker=_marker, _encumbrance=_encumbrance, _type="off_hand", _in_inventory_markers=["█","█", "◹", "◸"], _in_inventory_marker_positions=[(0,0),(0,1),(1,0),(1,1)], **kwargs)
        '''
       ▐▓▓▓▍
        ▜▓▛
        ▝▀▘
        ⩌⨷⨁
        '''
        self.eq_description = f"Action: Parry"

    def requisites(self, user):
        return "parry" in user.game_class.class_actions
 

   

