import item


def longSword(_location=None):
    return item.Sword(_name="Long Sword", _location=_location, _description="The crawler\"s best friend", _dmg=(1, 8), _rarity="common")

def warHammer(_location=None):
    return item.Hammer(_name="War Hammer", _location=_location, _description="Ready to tear down", _dmg=(2, 4), _rarity="rare")

def longBow(_location=None):
    return item.Bow(_name="Long Bow", _location=_location, _description="The crawler\"s long friend", _dmg=(1, 6), _rarity="uncommon")

def chainArmor(_location=None):
    return item.Armor(_name="Chain Armor", _location=_location, _bonus={"DEX":-2}, _dmg_reduction=1, _description="Tough and heavy, but it\'s groovy", _rarity="common")

def chiappilArmor(_location=None):
    return item.Armor(_name="Chiappilarmor", _location=_location, _bonus={"DEX":4}, _dmg_reduction=0, _description="Vai vai...", _rarity="rare")

def buckler(_location=None):
    return item.Shield(_name="Buckler", _location=_location, _description="A small, round shield", _rarity="common")

def rovaisThorn(_location=None):
    return item.Sword(_name="Rovai\'s Thorn", _location=_location, _bonus={"STR":4, "INT": 6}, _description="Robbosi si nasce", _dmg=(2, 8), _rarity="unique")


def healingPotion(_location=None):
    return item.Potion(_name="HP Potion", _location=_location, _effect={"HP":4}, _description="Heal 4 hit points", _rarity="common")