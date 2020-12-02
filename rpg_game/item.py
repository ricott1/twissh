import ability, uuid
     
class Item(object):
    def __init__(self, location=None, position = (0,0), marker = "i"):
        self.name = None
        self.type = None
        self.id = uuid.uuid4()
        self.marker = marker
        self.description = [""]
        self.rarity = "common" #common, uncommon, rare, unique, set
        self.position = position
        self.location = location
        self.bonus = {"MP" : 0, "HP" : 0, "HB" : 0, "RES" : 0, "STR" : 0, "DEX" : 0, "SPD" : 0, "MAG" : 0, "RTM" : 0, "AC" : 0}
        self.is_equipment = False
        self.is_equipped = False
        self.immunities = {}
        self.abilities = {}
    def on_equip(self, char):
        self.is_equipped = True
    def on_unequip(self, char): 
        self.is_equipped = False
    def on_update(self, *args):
        pass    
    def requisites(self, *args):
        return True

class Armor(Item):
    def __init__(self, name="", description=[""], bonus={}, location=None):
        super(Armor, self).__init__(location)
        self.name = name
        self.type = "Armor"
        self.is_equipment = True
        self.description = description
        self.bonus.update(bonus)

class Helm(Item):
    def __init__(self, name="", description=[""], bonus={}, location=None):
        super(Helm, self).__init__(location)
        self.name = name
        self.type = "Helm"
        self.is_equipment = True
        self.description = description
        self.bonus.update(bonus)
        
class Boots(Item):
    def __init__(self, name="", description=[""], bonus={}, location=None):
        super(Boots, self).__init__(location)
        self.name = name
        self.type = "Boots"
        self.is_equipment = True
        self.description = description
        self.bonus.update(bonus)    
        
class Gloves(Item):
    def __init__(self, name="", description=[""], bonus={}, location=None):
        super(Gloves, self).__init__(location)
        self.name = name
        self.type = "Gloves"
        self.is_equipment = True
        self.description = description
        self.bonus.update(bonus)  

class Belt(Item):
    def __init__(self, name="", description=[""], bonus={}, location=None):
        super(Belt, self).__init__(location)
        self.name = name
        self.type = "Belt"
        self.is_equipment = True
        self.description = description
        self.bonus.update(bonus) 
    
class Weapon(Item):
    def __init__(self, name="", description=[""], bonus={}, damage=6, dices=1, location=None):
        super(Weapon, self).__init__(location)
        self.name = name
        self.type = "Weapon"
        self.is_equipment = True
        self.description = description
        self.damage = damage
        self.dices = dices
        self.bonus.update({"DMG" : "{}d{}".format(self.dices, self.damage)})
        self.bonus.update(bonus)
 
   

