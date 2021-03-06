import character
from rpg_game.utils import random_stats, random_name
import random

# class Goblin(character.Monster):
#     """docstring for Goblin"""
#     def __init__(self, _name="goblin", **kwargs):
#         super().__init__(_name=_name, **kwargs)
#         self.DEX._value = max(14, self.DEX._value)

def goblin(_name="goblin", _stats=random_stats(), _location=None, **kwargs):
    monster = character.Monster(_name=_name, _stats=_stats, _location=_location, **kwargs)
    monster.DEX._value = max(14, monster.DEX._value)
    return monster

# class Ogre(character.Monster):
#     """docstring for Goblin"""
#     def __init__(self, _name="ogre", **kwargs):
#         super().__init__(_name=_name, _extra_positions=[(1,0,0), (1,1,0), (0,1,0)], **kwargs)
#         self.CON._value = max(18, self.CON._value)
#         self.HP._value = random.randint(3, 6) + self.HP._value

#     @property
#     def marker(self):
#         if self.is_dead:
#             return ["\\", "X", "\\", "X"]
#         return ["\\", "/", "\\", "/"]

# class Dragon(character.Monster):
#     """docstring for Goblin"""
#     def __init__(self, _name="dragon", **kwargs):
#         e_pos = [(1,0,0),(2,0,0)]
#         super().__init__(_name=_name, _extra_positions=e_pos, **kwargs)
#         self.CON._value = max(18, self.CON._value)
#         self.HP._value = random.randint(3, 6) + self.HP._value
#         print("DRAGON", self.positions)
#         self.direction_markers = {"up":["O","─","║"], "down":["O","-","║"], "left":["O","│","═"], "right":["O","│","═"]}

#     @property
#     def marker(self):
#         if self.is_dead:
#             return [
# "X", "/", "|", "x", "|", "\\",
# "|","/","v","|","v","\\","|",
# "-"
# ]
#         return [
# 		    "O", 
#   "/", "|", "-", "|", "\\",
# "⦬","/","v","║","v","\\","⦭",
#             "v"
# ]

# class Dragon(character.Monster):
#     """docstring for Goblin"""
#     def __init__(self, _name="dragon", **kwargs):
#         e_pos = [
#         (1,-2,1), (1,-1,0), (1,0,0), (1,1,0), (1,2,1),
#         (2, -3, 1), (2,-2,1), (2,-1,0), (2,0,0), (2,1,0), (2,2,1), (2,3,1),(3,0,0)]
#         super().__init__(_name=_name, _extra_positions=e_pos, **kwargs)
#         self.CON._value = max(18, self.CON._value)
#         self.HP._value = random.randint(3, 6) + self.HP._value
#         print("DRAGON", self.positions)

#     @property
#     def marker(self):
#         if self.is_dead:
#             return [
# "X", "/", "|", "x", "|", "\\",
# "|","/","v","|","v","\\","|",
# "-"
# ]
#         return [
#             "O", 
#   "/", "|", "-", "|", "\\",
# "⦬","/","v","║","v","\\","⦭",
#             "v"
# ]
