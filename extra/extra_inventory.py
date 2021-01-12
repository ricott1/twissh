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
    def __init__(self, name="Helm of Continency", description=["A monk cast helm"], bonus={"HB" : -12, "CON" : +2, "AC" : 1}, location=None):
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
        self.bonus["CON"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["CON"] = +2
        else:
            self.bonus["CON"] = 0
class JacksonBelt(item.Belt):
    def __init__(self, name="Jackson Belt", description=["Belt that belonged to Jackson", "Part of Jackson set"], bonus={}, location=None):
        super(JacksonBelt, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "set"
    def on_unequip(self, char): 
        self.is_equipped = False 
        self.bonus["CON"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["CON"] = +2
        else:
            self.bonus["CON"] = 0

class JacksonBoots(item.Boots):
    def __init__(self, name="Jackson Boots", description=["Boots that belonged to Jackson", "Part of Jackson set"], bonus={"SPD" : 1}, location=None):
        super(JacksonBoots, self).__init__(name=name, description=description, bonus=bonus, location=location)
        self.rarity = "set"
    def on_unequip(self, char): 
        self.is_equipped = False 
        self.bonus["CON"] = 0
    def on_update(self, DELTATIME, player):
        my_set = ["Jackson Helm", "Jackson Belt", "Jackson Boots"]
        if set(my_set) <= set([eq.name for (k, eq) in player.equipment.items()]):
            self.bonus["CON"] = +2
        else:
            self.bonus["CON"] = 0



PREFIX = ['']

SUFFIX = ['of vengeance','of delivery', 'of guidance']
def generate_item(typ='Armor', level=1, rarity='common'):
    if typ == 'Armor':
        name = random.sample(PREFIX, 1)[0] + 'Armor'
        if rarity == 'rare':
            name += random.sample(SUFFIX, 1)[0]
            bonus
        return item.Armor(name=name, description='', bonus=bonus, location = None)
