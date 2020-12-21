import action

class GameClass(object):
    def __init__(self):
        self.name = None

    @property
    def actions(self):
        return {"attack" : action.Attack, "move_up": action.MoveUp, "move_down": action.MoveDown, "move_left": action.MoveLeft, "move_right": action.MoveRight, "pick_up": action.PickUp, "drop": action.Drop}
        
    def requisites(self, *args):
        return True

class Novice(GameClass):
    def __init__(self):
        self.name = "novice"

    @property
    def actions(self):
        return {**super().actions, **{}}

class Warrior(GameClass):
    def __init__(self):
        self.name = "warrior"

    @property
    def actions(self):
        return {**super().actions, **{"parry" : action.Parry, "fire" : action.Fire}}