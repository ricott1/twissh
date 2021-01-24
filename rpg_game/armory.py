import item


def longSword(_location=None):
    return item.Sword(_name="Long Sword", _location=_location, _description="The crawler\"s best friend", _dmg=(1, 8), _rarity="common")

def dagger(_location=None):
    return item.Sword(_name="Dagger", _encumbrance=2, _location=_location, _speed=0.5, _description="So easy to lose", _dmg=(1, 4), _rarity="common")

def warHammer(_location=None):
    return item.Hammer(_name="War Hammer", _range=2, _location=_location, _description="Ready to tear down", _dmg=(2, 4), _rarity="rare")

def greatAxe(_location=None):
    return item.Hammer(_name="Great Axe", _range=1, _location=_location, _description="Chop it like it\'s hot", _dmg=(1, 12), _rarity="rare")

def shortBow(_location=None):
    return item.Bow(_name="Short Bow", _range=6, _location=_location, _description="The crawler\"s short friend", _dmg=(1, 6), _rarity="uncommon")

def longBow(_location=None):
    return item.Bow(_name="Long Bow", _range=8, _location=_location, _description="The crawler\"s long friend", _dmg=(1, 6), _rarity="uncommon")

def sniperBow(_location=None):
    return item.Bow(_name="Sniper Bow", _range=12, _speed=1.5, _location=_location, _description="Long range bow", _dmg=(1, 8), _rarity="rare")

def chainArmor(_location=None):
    return item.Armor(_name="Chain Armor", _location=_location, _bonus={"DEX":-2}, _dmg_reduction=1, _description="Tough and heavy, but it\'s groovy", _rarity="common")

def chiappilArmor(_location=None):
    return item.Armor(_name="Chiappilarmor", _location=_location, _bonus={"DEX":4}, _dmg_reduction=0, _description="Vai vai...", _rarity="rare")

def buckler(_location=None):
    return item.Shield(_name="Buckler", _location=_location, _description="A small, round shield", _rarity="uncommon")

def rovaisThorn(_location=None):
    return item.Sword(_name="Rovai\'s Thorn", _location=_location, _bonus={"STR":4, "INT": 6}, _description="Robbosi si nasce", _dmg=(2, 8), _rarity="set")

def woodenHelm(_location=None):
    return item.Helm(_name="Wooden Helm", _location=_location, _description="A light and stinky helmet", _rarity="common")

# def velvetGloves(_location=None):
#     return item.Gloves(_name="Velvet Gloves", _location=_location, _description="Fancy and useless", _rarity="common")

# def rovaisGloves(_location=None):
#     return item.Gloves(_name="Rovai\'s Gloves", _location=_location, _description="Fingerless denim gloves", _rarity="set")

def rovaisFlipFlops(_location=None):
    return item.Boots(_name="Rovai\'s Flip Flops", _location=_location, _description="As comfy as they look", _rarity="set")

def healingPotion(_location=None):
    return item.Potion(_name="HP Potion", _location=_location, _effect={"HP":4}, _description="Heal 4 hit points", _rarity="common")


def inventory_list(): 
    return {"common": [longSword, chainArmor, woodenHelm, healingPotion],
            "uncommon": [shortBow, longBow, buckler],
            "rare": [warHammer, sniperBow, chiappilArmor, greatAxe],
            "unique": [rovaisThorn, rovaisFlipFlops]}

