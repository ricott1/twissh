import item, random
import ability


class ShortSword(item.Weapon):
    def __init__(self):
        super(ShortSword, self).__init__(name="Short sword", description=[""], bonus={}, damage=6, dices=1, location=None)
        
class LongSword(item.Weapon):
    def __init__(self):
        super(LongSword, self).__init__(name="Long sword", description=[""], bonus={}, damage=8, dices=1, location=None)

class Dagger(item.Weapon):
    def __init__(self):
        super(Dagger, self).__init__(name="Dagger", description=[""], bonus={}, damage=4, dices=1, location=None)

class Axe(item.Weapon):
    def __init__(self):
        super(Axe, self).__init__(name="Axe", description=[""], bonus={"SPD" : -2}, damage=10, dices=1, location=None)

class LeatherArmor(item.Armor):
    def __init__(self):
        super(LeatherArmor, self).__init__(name="Leather Armor", description=["A leather armor"], bonus={"AC" : 2}, location=None)

class ChainArmor(item.Armor):
    def __init__(self, name="Chain Armor", description=["A chain armor"], bonus={"SPD" : -2, "AC" : 6}, location=None):
        super(ChainArmor, self).__init__(name=name, description=description, bonus=bonus, location=location)
    def requisites(self, player):
        if not player.job.name == "Assassin":   
            return True
        return False
class FuryArmor(item.Armor):
    def __init__(self, name="Fury Armor", description=["A cringeworthy armor"], bonus={"RES" : +1, "AC" : 2, "HB" : 8}, location=None):
        super(FuryArmor, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.abilities.update({"support" :  ability.Frenzy()})
        self.rarity = "uncommon"
    def requisites(self, player):
        #if player.job.name == "Barbarian":   
        return True
        #return False
        
class LongSword(item.Weapon):
    def __init__(self, name="Long Sword", description=["The crawler\"s best friend"], bonus={}, dices=1, damage=8, location=None):
        super(LongSword, self).__init__(name=name, description=description, bonus=bonus, dices=dices, damage=damage,  location=location)
    
    def requisites(self, player):
        if player.job.name == "Barbarian" or player.job.name == "Assassin" or player.job.name == "Protector" or player.job.name == "Wanderer" or player.race.name == "Elf":   
            return True
        return False
        
class GreatAxe(item.Weapon):
    def __init__(self, name="Great Axe", description=["Just a big ass axe"], bonus={"SPD" : -2}, dices=3, damage=4, location=None):
        super(GreatAxe, self).__init__(name=name, description=description, bonus=bonus, dices=dices, damage=damage,  location=location)
        self.rarity = "uncommon"
    def requisites(self, player):
        if player.job.name == "Barbarian" or player.race.name == "Dwarf":   
            return True
        return False       

class BeltOfGiants(item.Belt):
    def __init__(self, name="Belt of Giants", description=["Legendary belt crafted by the giants (although is very small)"], bonus={"SPD" : -2, "STR" : +4, "AC" : 1}, location=None):
        super(BeltOfGiants, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "unique"
    def requisites(self, player):
        return True

class HelmOfContinency(item.Helm):
    def __init__(self, name="Helm of Continency", description=["A monk cast helm"], bonus={"HB" : -12, "RES" : +2, "AC" : 1}, location=None):
        super(HelmOfContinency, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "rare"
    def requisites(self, player):
        return True         

class JacksonHelm(item.Helm):
    def __init__(self, name="Jackson Helm", description=["Helm that belonged to Jackson", "Part of Jackson set"], bonus={"AC" : 1}, location=None):
        super(JacksonHelm, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "set"
    def on_unequip(self, char): 
        self.is_equipped = False 
        self.bonus["RES"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["RES"] = +2
        else:
            self.bonus["RES"] = 0
class JacksonBelt(item.Belt):
    def __init__(self, name="Jackson Belt", description=["Belt that belonged to Jackson", "Part of Jackson set"], bonus={}, location=None):
        super(JacksonBelt, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "set"
    def on_unequip(self, char): 
        self.is_equipped = False 
        self.bonus["RES"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["RES"] = +2
        else:
            self.bonus["RES"] = 0

class JacksonBoots(item.Boots):
    def __init__(self, name="Jackson Boots", description=["Boots that belonged to Jackson", "Part of Jackson set"], bonus={"SPD" : 1}, location=None):
        super(JacksonBoots, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "set"
    def on_unequip(self, char): 
        self.is_equipped = False 
        self.bonus["RES"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["RES"] = +2
        else:
            self.bonus["RES"] = 0



PREFIX = ['']

SUFFIX = ['of vengeance','of delivery', 'of guidance']
def generate_item(typ='Armor', level=1, rarity='common'):
    if typ == 'Armor':
        name = random.sample(PREFIX, 1)[0] + 'Armor'
        if rarity == 'rare':
            name += random.sample(SUFFIX, 1)[0]
            bonus
        return item.Armor(name=name, description='', bonus=bonus, location = None)
