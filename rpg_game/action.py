import random, copy
from rpg_game.utils import roll1d20, roll1d4, roll
from rpg_game.constants import *
import item, character, entity

class Action(object):
    """implements rigid body properties"""
    name = ""
    recoil_cost = 0
    description = [""]

    @classmethod
    def use(cls):
        """Use action"""
        pass

    @classmethod
    def on_start(cls):
        """On start effects"""
        pass

    @classmethod
    def on_update(cls, DELTATIME):
        """On update effects"""
        pass

    @classmethod
    def on_end(cls):
        """On end effects"""
        pass

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        return user.forward

    @classmethod
    def action_direction(cls, user):
        x, y, z = user.position
        xt, yt, zt = cls.target_square(user)
        if (xt > x) and (yt == y):
            return "left"
        elif (xt < x) and (yt == y):
            return "right"
        elif (xt == x) and (yt > y):
            return "up"
        elif (xt == x) and (yt < y):
            return "down"

    @classmethod
    def target(cls, user):
        """Get action target square"""
        return user.location.get(cls.target_square(user))


    @classmethod
    def is_legal(cls, user):
        """Defines action legality"""
        return user.recoil == 0

class Move(Action):
    name = "move"
    recoil_cost = SHORT_RECOIL
    description = ["Step forward"]
    direction = None

    @classmethod
    def is_legal(cls, user, target):
        """Defines action legality"""
        return super().is_legal(user) and not target

    @classmethod
    def use(cls, user):
        if user.direction != cls.direction:
            #turning cost no recoil
            user.direction = cls.direction
            user.location.redraw = True
        target = cls.target(user)
        if cls.is_legal(user, target):
            user.location.clear(user.position)
            user.position = cls.target_square(user)
            user.location.register(user)
            user.recoil += cls.recoil_cost / user.movement_speed

class MoveUp(Move):
    name = "move_up"
    description = ["Step up"]
    direction = "up"

class MoveDown(Move):
    name = "move_down"
    description = ["Step down"]
    direction = "down"

class MoveLeft(Move):
    name = "move_left"
    description = ["Step left"]
    direction = "left"

class MoveRight(Move):
    name = "move_right"
    description = ["Step right"]
    direction = "right"

    

class PickUp(Action):
    name = "pick_up"
    recoil_cost = MED_RECOIL
    description = ["Pick up item"]

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def is_legal(cls, user, target):
        """Defines action legality"""
        return super().is_legal(user) and isinstance(target, item.Item)

    @classmethod
    def use(cls, user):
        target = cls.target(user)
        if cls.is_legal(user, target):
            user.add_inventory(target)
            user.recoil += cls.recoil_cost
            user.print_action = "Picked up: {}".format(target.name)


class Drop(Action):
    name = "drop"
    recoil_cost = SHORT_RECOIL
    description = ["Drop item"]

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def is_legal(cls, user, target, obj):
        """Defines action legality"""
        return super().is_legal(user) and not target and isinstance(obj, item.Item)

    @classmethod
    def use(cls, user, obj=None):
        if not obj:
            return
        target = cls.target(user)
        if cls.is_legal(user, target, obj):
            user.remove_inventory(obj)
            user.recoil += cls.recoil_cost
            user.print_action = "Dropped: {}".format(obj.name)

class Attack(Action):
    name = "attack"
    recoil_cost = LONG_RECOIL
    description = ["Basic attack"]

    @classmethod
    def is_legal(cls, user, target):
        """Defines action legality"""
        return super().is_legal(user) and isinstance(target, character.Character)

    @classmethod
    def use(cls, user):
        weapon = user.equipment["main_hand"]#use weapon range
        target = cls.target(user)
        if cls.is_legal(user, target):
            user.recoil += cls.recoil_cost
            if target.is_dead:
                user.print_action = f"Attack {target.name}: it's already dead!"
                return

            base = user.STR.mod
            if weapon:
                num, dice = weapon.dmg
            else:
                num, dice = (1, 4)

            r = roll1d20()
            if r == 20:
                dmg = max(1, roll(num, dice) + roll(num, dice) + base)
                target.hit(dmg)
                user.print_action = f"Attack {target.name}: critical! {dmg} damage{'s'*int(dmg>1)}!"
            elif target.action_counters["parry"]>0 and target.direction == cls.action_direction(user):
                user.print_action = f"Attack {target.name}: blocked!"
                target.print_action = f"Parry {user.name} attack!"
                target.action_counters["parry"] = 0
            elif r !=1:
                dmg = max(1, roll(num, dice) + base)
                target.hit(dmg)
                user.print_action = f"Attack {target.name}: {dmg} damage{'s'*int(dmg>1)}!"
            else:
                user.print_action = f"Attack {target.name}: misses!"

class Parry(Action):
    name = "parry"
    recoil_cost = SHORT_RECOIL
    description = ["Parry attacks"]
    #PARRY_INTERVAL = 5#for testing, should be 1

    @classmethod
    def is_legal(cls, user):
        """Defines action legality"""
        return super().is_legal(user) and user.action_counters["parry"] == 0

    @classmethod
    def use(cls, user):
        if cls.is_legal(user):
            user.action_counters["parry"] += cls.recoil_cost
            user.recoil += cls.recoil_cost

class Fire(Action):
    name = "fire"
    recoil_cost = LONG_RECOIL
    description = ["Fire arrow"]
    #PARRY_INTERVAL = 5#for testing, should be 1

    @classmethod
    def is_legal(cls, user):
        """Defines action legality"""
        return super().is_legal(user) and user.location.is_empty(user.forward)

    @classmethod
    def hit(cls, proj):
        num, dice = (1, 4)
        base = 0
        target = proj.location.get(proj.forward)
        if not isinstance(target, character.Character):
            return
        r = roll1d20()
        if r == 20:
            dmg = max(1, roll(num, dice) + roll(num, dice) + base)
            target.hit(dmg)
            proj.spawner.print_action = f"Attack {target.name}: critical! {dmg} damage{'s'*int(dmg>1)}!"
        elif target.action_counters["parry"]>0:# and target.direction == cls.action_direction(proj):
            proj.spawner.print_action = f"Attack {target.name}: blocked!"
            target.print_action = f"Parry {proj.spawner.name}\'s arrow!"
            target.action_counters["parry"] = 0
        elif r !=1:
            dmg = max(1, roll(num, dice) + base)
            target.hit(dmg)
            proj.spawner.print_action = f"Attack {target.name}: {dmg} damage{'s'*int(dmg>1)}!"
        else:
            proj.spawner.print_action = f"Attack {target.name}: misses!"

    @classmethod
    def use(cls, user):
        if cls.is_legal(user):
            proj = entity.Projectile(_spawner = user, _direction=user.direction, _position=user.forward, _location=user.location, _on_hit=cls.hit)
            user.recoil += cls.recoil_cost


