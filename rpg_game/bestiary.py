from character import Villain
import random

class Goblin(Villain):
    """docstring for Goblin"""
    def __init__(self, **kwargs):
        super().__init__(_name="goblin", **kwargs)
        self.DEX.value = max(14, self.DEX.value)

class Ogre(Villain):
    """docstring for Goblin"""
    def __init__(self, **kwargs):
        super().__init__(_name="dragon", _extra_position=[(1,0,0), (1,1,0), (0,1,0)], **kwargs)
        self.CON.value = max(18, self.CON.value)
        self.HP.value = random.randint(3, 6) + self.HP.value

    @property
    def marker(self):
        if self.is_dead:
            return ["\\", "X", "\\", "X"]
        return ["\\", "/", "\\", "/"]

class Dragon(Villain):
    """docstring for Goblin"""
    def __init__(self, **kwargs):
        e_pos = [
        (1,-2,0), (1,-1,0), (1,0,0), (1,1,0), (1,2,0),
        (2, -3, 0), (2,-2,0), (2,-1,0), (2,0,0), (2,1,0), (2,2,0), (2,3,0),(3,0,0)]
        super().__init__(_name="dragon", _extra_position=e_pos, **kwargs)
        self.CON.value = max(18, self.CON.value)
        self.HP.value = random.randint(3, 6) + self.HP.value

    @property
    def marker(self):
        if self.is_dead:
            return [
"X", "/", "|", "x", "|", "\\",
"|","/","v","|","v","\\","|",
"-"
]
        return [
		"O", 
"/", "|", "-", "|", "\\",
"⦬","/","v","|","v","\\","⦭",
"v"
]

# 🔥
#    O
#  /|-|\
# ⦬/v|v\⦭
#    v
# ⩘⟇⟑⩺⩹⦨⦩⦪⦫⦬⦭⦮⦯
#    
#  /|-|\
# |/v|v\|
#    v 
