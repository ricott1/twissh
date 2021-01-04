import item

        
class LongSword(item.Weapon):
    def __init__(self, **kwargs):
        super().__init__(_name="Long Sword", _description=["The crawler\"s best friend"], _dmg=(1, 8),  **kwargs)
        self.rarity = "common"

class LongBow(item.Bow):
    def __init__(self, **kwargs):
        super().__init__(_name="Long Bow", _description=["The crawler\"s long friend"], _dmg=(1, 4),  **kwargs)
        self.rarity = "common"

class ChainArmor(item.Armor):
    def __init__(self,  **kwargs):
        super().__init__(_name="Chain Armor", _bonus={"DEX":-2}, _dmg_reduction=1, _description=["Tough and heavy, but it\'s groovy"],  **kwargs)
        self.rarity = "uncommon"

class ChiappilArmor(item.Armor):
    def __init__(self,  **kwargs):
        super().__init__(_name="Chiappil Armor", _bonus={"DEX":4}, _dmg_reduction=0, _description=["Vai vai..."],  **kwargs)
        self.rarity = "uncommon"

class Buckler(item.Shield):
    def __init__(self,  **kwargs):
        super().__init__(_name="Buckler", _description=["A small, round shield"],  **kwargs)
        self.rarity = "uncommon"

class RovaisThorn(item.Weapon):
    def __init__(self, **kwargs):
        super().__init__(_name="Rovai\'s Thorn", _bonus={"STR":4, "INT": 6}, _description=["Robbosi si nasce"], _dmg=(2, 8),  **kwargs)
        self.rarity = "rare"