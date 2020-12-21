import item

        
class LongSword(item.Weapon):
    def __init__(self, **kwargs):
        super().__init__(_name="Long Sword", _description=["The crawler\"s best friend"], _dmg=(1, 8),  **kwargs)
        self.rarity = "uncommon"

class ChainArmor(item.Armor):
    def __init__(self,  **kwargs):
        super().__init__(_name="Chain Armor", _dmg_reduction=1, _description=["Tough and heavy, but it\'s groovy"],  **kwargs)
        self.rarity = "unique"
