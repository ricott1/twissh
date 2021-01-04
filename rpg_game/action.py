import random, copy
from rpg_game.utils import roll1d20, roll1d4, roll
from rpg_game.constants import *
import item, character, entity

class Action(object):
    """implements rigid body properties"""
    name = ""
    recoil_cost = 0
    description = ""

    @classmethod
    def use(cls):
        """Use action"""
        pass

    @classmethod
    def on_start(cls):
        """On start effects"""
        pass

    @classmethod
    def on_update(cls, user, DELTATIME):
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
        if (xt < x) and (yt == y):
            return "down"
        elif (xt > x) and (yt == y):
            return "up"
        elif (xt == x) and (yt < y):
            return "right"
        elif (xt == x) and (yt > y):
            return "left"

    @classmethod
    def target(cls, user):
        """Get action target square"""
        return user.location.get(cls.target_square(user))


    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return user.recoil == 0 and not user.is_dead

class Move(Action):
    name = "move"
    recoil_cost = SHORT_RECOIL
    description = "Move forward"
    direction = None

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return user.movement_recoil == 0 and not user.is_dead

    @classmethod
    def use(cls, user):
        if not cls.requisites(user):
            return
        if user.direction != cls.direction:
            #turning cost no recoil
            #user.movement_recoil += MIN_RECOIL
            user.direction = cls.direction
            user.location.redraw = True
        else:
            user.direction = cls.direction
            delta_x = int(user.direction=="down") - int(user.direction=="up")
            delta_y = int(user.direction=="right") - int(user.direction=="left")
            for xp, yp, zp in user.positions:
                t = user.location.get((delta_x+xp, delta_y+yp, zp))
                if t not in (None, user):
                    return
            x, y, z = user.position
            user.position = (x + delta_x, y + delta_y, z)
            user.recoil += MIN_RECOIL
            user.movement_recoil += SHORTER_RECOIL


class MoveUp(Move):
    name = "move_up"
    description = "Move up"
    direction = "up"

class MoveDown(Move):
    name = "move_down"
    description = "Move down"
    direction = "down"

class MoveLeft(Move):
    name = "move_left"
    description = "Move left"
    direction = "left"

class MoveRight(Move):
    name = "move_right"
    description = "Move right"
    direction = "right"

class Dash(Action):
    name = "dash"
    recoil_cost = SHORT_RECOIL
    description = "Dash forward"
    direction = None

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return user.movement_recoil == 0 and not user.is_dead

    @classmethod
    def use(cls, user):
        if not cls.requisites(user):
            return
        
        user.direction = cls.direction
        delta_x = int(user.direction=="down") - int(user.direction=="up")
        delta_y = int(user.direction=="right") - int(user.direction=="left")
        for xp, yp, zp in user.positions:
            t = user.location.get((delta_x+xp, delta_y+yp, zp))
            if t not in (None, user):
                return
        x, y, z = user.position
        user.position = (x + delta_x, y + delta_y, z)
        user.recoil += SHORTER_RECOIL
        user.movement_recoil += SHORTER_RECOIL/user.movement_speed


class DashUp(Dash):
    name = "dash_up"
    description = "Dash up"
    direction = "up"

class DashDown(Dash):
    name = "dash_down"
    description = "Dash down"
    direction = "down"

class DashLeft(Dash):
    name = "dash_left"
    description = "Dash left"
    direction = "left"

class DashRight(Dash):
    name = "dash_right"
    description = "Dash right"
    direction = "right"


class PickUp(Action):
    name = "pick_up"
    recoil_cost = MED_RECOIL
    description = "Pick up item"

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def requisites(cls, user, target):
        """Defines action legality"""
        return super().requisites(user) and isinstance(target, item.Item)

    @classmethod
    def use(cls, user):
        target = cls.target(user)
        if cls.requisites(user, target):
            user.add_inventory(target)
            user.recoil += cls.recoil_cost
            user.print_action = "Picked up: {}".format(target.name)


class Drop(Action):
    name = "drop"
    recoil_cost = SHORT_RECOIL
    description = "Drop item"

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def requisites(cls, user, target, obj):
        """Defines action legality"""
        return super().requisites(user) and not target and isinstance(obj, item.Item)

    @classmethod
    def use(cls, user, obj=None):
        if not obj:
            return
        target = cls.target(user)
        if cls.requisites(user, target, obj):
            user.remove_inventory(obj)
            user.recoil += cls.recoil_cost
            user.print_action = "Dropped: {}".format(obj.name)

class Attack(Action):
    name = "attack"
    recoil_cost = LONG_RECOIL
    description = "Attack"

    @classmethod
    def requisites(cls, user, target):
        """Defines action legality"""
        return super().requisites(user) and isinstance(target, character.Character)

    @classmethod
    def use(cls, user):
        weapon = user.equipment["main_hand"]#use weapon range
        target = cls.target(user)
        if cls.requisites(user, target):
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
            print("ATTACK", cls.action_direction(user), target.direction)
            user.action_marker = {"up":"⩓", "down":"⩔", "left":"⪡", "right":"⪢", "time":SHORT_RECOIL}
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
    description = "Parry"
    #PARRY_INTERVAL = 5#for testing, should be 1

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and user.action_counters["parry"] == 0 and isinstance(user.equipment["off_hand"], item.Shield)

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            user.action_counters["parry"] += SHORT_RECOIL
            user.recoil += MED_RECOIL
            user.action_marker = {"up":"◠", "down":"◡", "left":"(", "right":")", "time":SHORT_RECOIL}

class Arrow(Action):
    name = "arrow"
    recoil_cost = LONG_RECOIL
    description = "Fire arrow"
    #PARRY_INTERVAL = 5#for testing, should be 1

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and user.location.is_empty(user.forward) and isinstance(user.equipment["main_hand"], item.Bow)

    @classmethod
    def hit(cls, proj):
        num, dice = (1, 4)
        base = proj.spawner.DEX.mod
        target = proj.location.get(proj.forward)
        if not isinstance(target, character.Character):
            return
        r = roll1d20()
        if r == 20:
            dmg = max(1, roll(num, dice) + roll(num, dice) + base)
            target.hit(dmg)
            proj.spawner.print_action = f"Attack {target.name}: critical! {dmg} damage{'s'*int(dmg>1)}!"
        elif target.action_counters["parry"]>0 and target.direction == cls.action_direction(proj):
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
        if cls.requisites(user):
            proj = entity.Arrow(_spawner = user, _on_hit=cls.hit)
            user.recoil += cls.recoil_cost

class FireBall(Action):
    name = "fire"
    recoil_cost = MAX_RECOIL
    description = "Just cast fireball"

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and user.location.is_empty(user.forward)

    @classmethod
    def hit(cls, proj):
        num, dice = (proj.fragment, 6)
        base = 0
        target = proj.location.get(proj.forward)
        if isinstance(target, character.Character):
            dmg = max(1, roll(num, dice) + base)
            target.hit(dmg)
            proj.spawner.print_action = f"FIREBALL in {target.name}\'s face: {dmg} damage{'s'*int(dmg>1)}!"
        
        if proj.fragment > 1:
            px, py, pz = proj.position
            print("SPLITTIN AT", proj.position)
            extra_pos = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
            for direction in extra_pos:
                x, y = extra_pos[direction]
                new_pos = (x+px, y+py, pz)
                if proj.location.is_empty(new_pos):
                    frag = entity.FireBall(_spawner = proj.spawner, _on_hit=cls.hit, _direction=direction, _position=new_pos, _fragment = proj.fragment - 1, _location=proj.location)
                    frag.max_range = frag.fragment

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            proj = entity.FireBall(_spawner = user, _on_hit=cls.hit, _direction=user.direction, _position=user.forward, _fragment = user.INT.mod + 1)
            user.recoil += cls.recoil_cost

class Teleport(Action):
    name = "teleport"
    recoil_cost = MAX_RECOIL
    description = "Teleport"

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            x, y, z = user.position
            new_pos = user.location.free_position(_layer=z)
            if new_pos:
                user.position = new_pos
                user.recoil += cls.recoil_cost

class Hide(Action):
    name = "hide"
    recoil_cost = MIN_RECOIL
    description = "Hide in shadows"

    @classmethod
    def on_update(cls, user, DELTATIME):
        """On update effects"""
        if user.action_counters["hide"] > 0:
            user.recoil += DELTATIME * (1 + cls.recoil_cost)

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and user.action_counters["hide"] == 0 and not user.equipment["body"]

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            user.action_counters["hide"] = MAX_RECOIL
            user.recoil += MED_RECOIL
            user.action_marker = {"up":" ", "down":" ", "left":" ", "right":" ", "time":MAX_RECOIL}
        elif user.action_counters["hide"] > 0:
            user.action_counters["hide"] = 0
            user.action_marker = {}


