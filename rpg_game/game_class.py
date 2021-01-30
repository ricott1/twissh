import action, armory

class GameClass(object):
    stats_level = {"STR":1, "INT":1, "WIS":1, "CON":1, "DEX":1, "CHA":1}
    def __init__(self):
        self.name = None
        self.base_actions = {"attack" : action.Attack, "move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight, "dash_up": action.DashUp, "dash_down": action.DashDown, "dash_left": action.DashLeft, "dash_right": action.DashRight, "consume" : action.Consume, "pick_up": action.PickUp, "drop": action.Drop, "equip": action.Equip, "unequip": action.Unequip}
        self.class_actions = {}
        self.class_input = {}
        self.bonus = {}
        self.initial_inventory = []

    @property
    def actions(self):
        return {**self.base_actions, **self.class_actions}
        
    def requisites(self, *args):
        return True


class Monster(GameClass):
    stats_level = {"STR":2, "INT":1, "WIS":1, "CON":2, "DEX":1, "CHA":1}
    def __init__(self):
        super().__init__()
        self.name = "monster"

class Wizard(GameClass):
    stats_level = {"STR":1, "INT":3, "WIS":2, "CON":1, "DEX":2, "CHA":2}
    def __init__(self):
        super().__init__()
        self.name = "wizard"
        self.class_actions = {"fireball" : action.FireBall, "teleport" : action.Teleport, "icewall" : action.IceWall}
        self.class_input = {"class_ability_1": "fireball", "class_ability_2": "teleport", "class_ability_3": "icewall"}
        self.bonus = {"INT": 1}

class Warrior(GameClass):
    stats_level = {"STR":3, "INT":1, "WIS":1, "CON":2, "DEX":1, "CHA":2}
    def __init__(self):
        super().__init__()
        self.name = "warrior"
        self.class_actions = {"parry" : action.Parry, "charge": action.Charge}
        self.class_input = {"class_ability_1": "parry", "class_ability_2": "charge"}
        self.bonus = {"HP": 4, "STR":1}
        self.initial_inventory = [armory.longSword, armory.longBow, armory.buckler]

class Dwarf(GameClass):
    stats_level = {"STR":3, "INT":2, "WIS":2, "CON":3, "DEX":1, "CHA":1}
    def __init__(self):
        super().__init__()
        self.name = "dwarf"
        self.base_actions["attack"] = action.Demolish
        self.class_actions = {"parry" : action.Parry}
        self.class_input = {"class_ability_1": "parry"}
        self.bonus = {"HP": 6, "STR":1, "CON":1, "encumbrance" : 4, "movement_speed":-0.25}
        self.initial_inventory = [armory.warHammer, armory.woodenHelm]

class Thief(GameClass):
    stats_level = {"STR":2, "INT":3, "WIS":1, "CON":2, "DEX":3, "CHA":1}
    def __init__(self):
        super().__init__()
        self.name = "thief"
        self.base_actions["attack"] = action.SneakAttack
        self.class_actions = {"hide" : action.Hide, "trap" : action.Trap}
        self.class_input = {"class_ability_1": "hide", "class_ability_2": "trap"}
        self.bonus = {"HP": 2, "DEX": 1, "INT": 1, "movement_speed":0.5}
        self.initial_inventory = [armory.dagger, armory.sniperBow]

class Bard(GameClass):
    stats_level = {"STR":1, "INT":3, "WIS":2, "CON":1, "DEX":3, "CHA":3}
    def __init__(self):
        super().__init__()
        self.name = "bard"
        self.class_actions = {"sing" : action.Sing, "summon" : action.Summon}
        self.class_input = {"class_ability_1": "sing", "class_ability_2": "summon"}
        self.initial_inventory = [armory.dagger]
        self.bonus = {"HP": 2, "CHA": 1, "INT": 1, "DEX": 1, "movement_speed":0.25}



