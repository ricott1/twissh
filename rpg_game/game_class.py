import action, inventory

class GameClass(object):
    def __init__(self):
        self.name = None
        self.base_actions = {"attack" : action.Attack, "move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight, "dash_up": action.DashUp, "dash_down": action.DashDown, "dash_left": action.DashLeft, "dash_right": action.DashRight, "consume" : action.Consume, "pick_up": action.PickUp, "drop": action.Drop}
        self.class_actions = {}
        self.bonus = {}
        self.initial_inventory = []

    @property
    def actions(self):
        return {**self.base_actions, **self.class_actions}
        
    def requisites(self, *args):
        return True

class Monster(GameClass):
    def __init__(self):
        super().__init__()
        self.base_actions = {"attack" : action.Attack, "move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight, "dash_up": action.DashUp, "dash_down": action.DashDown, "dash_left": action.DashLeft, "dash_right": action.DashRight, "pick_up": action.PickUp}
        self.name = "monster"


class Novice(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "novice"
        self.class_actions = {"fireball" : action.FireBall, "teleport" : action.Teleport, "icewall" : action.IceWall}
        self.bonus = {"INT": 1}

class Warrior(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "warrior"
        self.class_actions = {"parry" : action.Parry, "charge": action.Charge}
        self.bonus = {"HP": 4, "STR":1}

class Dwarf(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "dwarf"
        self.class_actions = {"parry" : action.Parry, "demolish": action.Demolish}
        self.bonus = {"HP": 6, "STR":1, "CON":1}
        self.initial_inventory = [inventory.warHammer, inventory.healingPotion]

class Thief(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "thief"
        self.class_actions = {"hide" : action.Hide, "trap" : action.Trap}
        self.bonus = {"HP": 2, "DEX": 1, "INT": 1}

class Bard(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "bard"
        self.class_actions = {"sing" : action.Sing}
        self.bonus = {"HP": 2, "CHA": 1, "INT": 1, "DEX": 1}



