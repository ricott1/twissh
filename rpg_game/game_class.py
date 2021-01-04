import action

class GameClass(object):
    def __init__(self):
        self.name = None
        self.base_actions = {"attack" : action.Attack, "move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight, "dash_up": action.DashUp, "dash_down": action.DashDown, "dash_left": action.DashLeft, "dash_right": action.DashRight, "pick_up": action.PickUp, "drop": action.Drop}
        self.class_actions = {}
        self.bonus = {}

    @property
    def actions(self):
        return {**self.base_actions, **self.class_actions}
        
    def requisites(self, *args):
        return True

class Monster(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "monster"


class Novice(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "novice"
        self.class_actions = {"fireball" : action.FireBall, "teleport" : action.Teleport}
        self.bonus = {"INT": 1}

class Warrior(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "warrior"
        self.class_actions = {"parry" : action.Parry, "arrow" : action.Arrow}
        self.bonus = {"HP": 6}

class Thief(GameClass):
    def __init__(self):
        super().__init__()
        self.name = "warrior"
        self.class_actions = {"hide" : action.Hide, "arrow" : action.Arrow}
        self.bonus = {"HP": 2, "DEX": 1}

