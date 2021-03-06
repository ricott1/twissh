from rpg_game.utils import roll1d20, roll1d4, roll
from rpg_game.constants import *
import counter, item, character, entity, bestiary

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
        return user.recoil == 0

class Move(Action):
    name = "move"
    recoil_cost = SHORT_RECOIL
    description = "Move forward"
    direction = None

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return user.movement_recoil == 0

    @classmethod
    def use(cls, user):
        if not cls.requisites(user):
            return
        if user.direction != cls.direction:
            
            #don't transform coordinates if facing down.
            if cls.direction == "down":
                _extra_positions = [(x, y, z) for x, y, z in user.extra_positions]
            elif cls.direction == "up":
                _extra_positions = [(-x, -y, z) for x, y, z in user.extra_positions]
            elif cls.direction == "right":
                _extra_positions = [(-y, x, z) for x, y, z in user.extra_positions]
            elif cls.direction == "left":
                _extra_positions = [(y, -x, z) for x, y, z in user.extra_positions]

            x, y, z = user.position
            for xp, yp, zp in _extra_positions:
                t = user.location.get((x+xp, y+yp, zp))
                if t not in (None, user):
                    return
            user.direction = cls.direction
        else:
            delta_x = int(user.direction=="down") - int(user.direction=="up")
            delta_y = int(user.direction=="right") - int(user.direction=="left")
            for xp, yp, zp in user.positions:
                t = user.location.get((delta_x+xp, delta_y+yp, zp))
                if t not in (None, user):
                    return
            x, y, z = user.position
            user.position = (x + delta_x, y + delta_y, z)
            user.recoil += MIN_RECOIL
            user.movement_recoil += SHORTER_RECOIL/(user.movement_speed)


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
        return user.movement_recoil == 0 and not user.slow_recovery

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
        user.movement_recoil += SHORTER_RECOIL/(DASH_SPEED_MULTI*user.movement_speed)


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
    recoil_cost = MIN_RECOIL
    description = "Pick up item"

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        target = cls.target(user)
        return super().requisites(user) and isinstance(target, item.Item)

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            target = cls.target(user)
            if not user.inventory.has_free_spot():
                counter.TextCounter(user, f"Inventory full")
                return
            if EXTRA_ENCUMBRANCE_MULTI*user.encumbrance < target.encumbrance + user.inventory.encumbrance:
                counter.TextCounter(user, f"Over encumbrance limit")
                return
            user.add_inventory(target)
            user.recoil += cls.recoil_cost
            if user.encumbrance < target.encumbrance + user.inventory.encumbrance:
                counter.TextCounter(user, f"Picked up: {target.name}; encumbered")
            else:
                counter.TextCounter(user, f"Picked up: {target.name}")

class Consume(Action):
    name = "consume"
    recoil_cost = MED_RECOIL
    description = "Consume item"


    @classmethod
    def requisites(cls, user, obj=None):
        """Defines action legality"""
        return super().requisites(user) and isinstance(obj, item.Consumable)

    @classmethod
    def use(cls, user, obj=None):
        obj = obj or user.inventory.selection
        if not obj:
            return
        if cls.requisites(user, obj):
            user.recoil += cls.recoil_cost
            counter.TextCounter(user, f"Consumed: {obj.name}")
            obj.on_use(user)

class Drop(Action):
    name = "drop"
    recoil_cost = MIN_RECOIL
    description = "Drop item"

    @classmethod
    def target_square(cls, user):
        """Get action target square"""
        x, y, z = user.position
        return (x, y, 0)

    @classmethod
    def requisites(cls, user, obj=None):
        """Defines action legality"""
        x, y, z = user.position
        return super().requisites(user) and user.location.is_empty((x, y, 0)) and isinstance(obj, item.Item) and obj.id in user.inventory.entities

    @classmethod
    def use(cls, user, obj=None):
        obj = obj or user.inventory.selection
        if not obj:
            return
        x, y, z = user.position
        if cls.requisites(user, obj):
            user.drop_inventory(obj)
            user.recoil += cls.recoil_cost
            counter.TextCounter(user, f"Dropped: {obj.name}")
        elif not user.location.is_empty((x, y, 0)):
                counter.TextCounter(user, f"Can\'t drop here")

class Equip(Action):
    name = "equip"
    recoil_cost = SHORT_RECOIL
    description = "Equip item"

    @classmethod
    def requisites(cls, user, obj=None):
        """Defines action legality"""
        x, y, z = user.position
        return super().requisites(user) and isinstance(obj, item.Item) and obj.is_equipment and obj.id in user.inventory.entities

    @classmethod
    def use(cls, user, obj=None):
        obj = obj or user.inventory.selection
        if not obj:
            return
        x, y, z = user.position
        if cls.requisites(user, obj):
            user.equip(obj)
            user.recoil += cls.recoil_cost

class Unequip(Action):
    name = "unequip"
    recoil_cost = SHORT_RECOIL
    description = "Unequip item"

    @classmethod
    def requisites(cls, user, obj=None):
        """Defines action legality"""
        x, y, z = user.position
        return super().requisites(user) and isinstance(obj, item.Item) and obj.is_equipment and obj.is_equipped

    @classmethod
    def use(cls, user, obj=None):
        obj = obj or user.inventory.selection
        if not obj:
            return
        x, y, z = user.position
        if cls.requisites(user, obj):
            user.unequip(obj)
            user.recoil += cls.recoil_cost

class Attack(Action):
    name = "attack"
    recoil_cost = LONG_RECOIL
    description = "Attack"

    @classmethod
    def target(cls, user):
        """Get action target square"""
        weapon = user.equipment["main_hand"]
        if weapon:
            _range = weapon.range
        else:
            _range = 1
        for s in range(1, _range+1):
            t = user.location.get(user.forward_by(s))
            
            if t:
                return t
        return None

    @classmethod
    def hit(cls, user, target):
        if target.is_dead:
            counter.TextCounter(user, f"Attack {target.name}: it's already dead!")
            return
        
        base = user.STR.mod
        weapon = user.equipment["main_hand"]
        if weapon:
            num, dice = weapon.dmg
            val, multi = weapon.critical
            speed = weapon.speed
        else:
            num, dice = (1, 4)
            val, multi = (20, 2)
            speed = BASE_ATTACK_SPEED

        user.recoil += cls.recoil_cost * speed

        r = roll1d20()
        counter.MarkerCounter(user, {k:[v for _ in user.positions] for k, v in zip(("up", "down", "left", "right"), ("⩓", "⩔", "⪡", "⪢"))}, SHORT_RECOIL)
        if r >= val:
            dmg = max(1, multi*roll(num, dice) + base)
            target.hit(dmg)
            if target.is_dead:
                user.exp += EXP_PER_KILL
            counter.TextCounter(user, f"Attack {target.name}: critical! {dmg} damage{'s'*int(dmg>1)}!")
        elif "parry" in target.counters and target.direction == cls.action_direction(user):
            counter.TextCounter(user, f"Attack {target.name}: blocked!")
            counter.TextCounter(target, f"Parry {user.name} attack!")
            user.recoil += SHORT_RECOIL
            target.counters["parry"].on_end()
        elif r !=1:
            dmg = max(1, roll(num, dice) + base)
            target.hit(dmg)
            if target.is_dead:
                user.exp += EXP_PER_KILL
            counter.TextCounter(user, f"Attack {target.name}: {dmg} damage{'s'*int(dmg>1)}!")
        else:
            counter.TextCounter(user, f"Attack {target.name}: misses!")

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        target = cls.target(user)
        return user.recoil == 0 and target

    @classmethod
    def use(cls, user):
        weapon = user.equipment["main_hand"]
        target = cls.target(user)
        if isinstance(weapon, item.Bow):
            Arrow.use(user)
        elif cls.requisites(user):
            target = cls.target(user)
            cls.hit(user, target)

class SneakAttack(Action):
    name = "sneak_attack"
    recoil_cost = LONG_RECOIL
    description = "Sneak attack"

    @classmethod
    def hit(cls, user, target):
        if target.is_dead:
            counter.TextCounter(user, f"Attack {target.name}: it's already dead!")
            return
        
        base = user.STR.mod
        weapon = user.equipment["main_hand"]
        num, dice = weapon.dmg
        val, multi = weapon.critical
        speed = weapon.speed
        user.recoil += cls.recoil_cost * weapon.speed

        if r >= val:
            dmg = max(1, multi*user.level * roll(num, dice) + base)
            target.hit(dmg)
            if target.is_dead:
                user.exp += EXP_PER_KILL
            counter.TextCounter(user, f"Critical Sneak {target.name}: {dmg} damage{'s'*int(dmg>1)}!")
        else:
            dmg = max(1, user.level * roll(num, dice) + base)
            target.hit(dmg)
            if target.is_dead:
                user.exp += EXP_PER_KILL
            counter.TextCounter(user, f"Sneak Attack {target.name}: {dmg} damage{'s'*int(dmg>1)}!")

        
        counter.MarkerCounter(user, {k:[v for _ in user.positions] for k, v in zip(("up", "down", "left", "right"), ("⩓", "⩔", "⪡", "⪢"))}, SHORT_RECOIL)
        
        

    @classmethod
    def target(cls, user):
        return Attack.target(user)

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return Attack.requisites(user)

    @classmethod
    def use(cls, user):
        weapon = user.equipment["main_hand"]
        target = cls.target(user)
        if isinstance(weapon, item.Bow):
            Arrow.use(user)
        elif cls.requisites(user):
            if target.direction == user.direction and isinstance(weapon, item.Sword) and isinstance(target, character.Character):
                cls.hit(user, target)
            else:
                Attack.hit(user, target)

class Demolish(Action):
    name = "demolish"
    recoil_cost = MED_RECOIL
    description = "Demolish"
    DEMOLISH_BONUS = 5

    @classmethod
    def hit(cls, user, target):
        base = user.STR.mod
        weapon = user.equipment["main_hand"]
        num, dice = weapon.dmg
        val, multi = weapon.critical
        speed = weapon.speed
        user.recoil += cls.recoil_cost * weapon.speed

        r = roll1d20()
        counter.MarkerCounter(user, {k:[v for _ in user.positions] for k, v in zip(("up", "down", "left", "right"), ("⩓", "⩔", "⪡", "⪢"))}, SHORT_RECOIL)
        if r >= val:
            dmg = target.HP.max
            target.hit(dmg)
            counter.TextCounter(user, f"Demolish {target.name}: demolished!")
        else:
            dmg = max(1, cls.DEMOLISH_BONUS*roll(num, dice) + base)
            target.hit(dmg)
            counter.TextCounter(user, f"Demolish {target.name}: {dmg} damage{'s'*int(dmg>1)}!")

    @classmethod
    def target(cls, user):
        return Attack.target(user)

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return Attack.requisites(user)

    @classmethod
    def use(cls, user):
        weapon = user.equipment["main_hand"]
        target = cls.target(user)
        if isinstance(weapon, item.Bow):
            Arrow.use(user)
        elif cls.requisites(user):
            if isinstance(weapon, item.Hammer) and isinstance(target, entity.ThinWall):
                cls.hit(user, target)
            else:
                Attack.hit(user, target)               

class Parry(Action):
    name = "parry"
    description = "Parry"
    PARRY_INTERVAL = SHORT_RECOIL

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and "parry" not in user.counters and isinstance(user.equipment["off_hand"], item.Shield)

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            counter.ParryCounter(user, cls.PARRY_INTERVAL)
            user.recoil += MED_RECOIL

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
        target = proj.location.get(proj.forward)
        if not target:
            return
        if target.is_dead:
            counter.TextCounter(proj.spawner, f"Attack {target.name}: it's already dead!")
            return
        r = roll1d20()
        if r >= proj.crit_range:
            dmg = proj.crit_dmg
            target.hit(dmg)
            if target.is_dead:
                proj.spawner.exp += EXP_PER_KILL
            counter.TextCounter(proj.spawner, f"Attack {target.name}: critical! {dmg} damage{'s'*int(dmg>1)}!")
        elif "parry" in target.counters and target.direction == cls.action_direction(proj):
            if target.DEX.mod >= 2:
                counter.TextCounter(proj.spawner, f"Attack {target.name}: blocked!")
                counter.TextCounter(target, f"Bounces {proj.spawner.name}\'s arrow back!")
                entity.Arrow(_spawner=target, _max_range=proj.max_range, _on_hit=proj.on_hit, _dmg=proj.dmg, _crit=proj.crit)
            else:
                counter.TextCounter(proj.spawner, f"Attack {target.name}: blocked!")
                counter.TextCounter(target, f"Parry {proj.spawner.name}\'s arrow")
            target.counters["parry"].on_end()
        elif r !=1:
            dmg = proj.dmg
            target.hit(dmg)
            if target.is_dead:
                proj.spawner.exp += EXP_PER_KILL
            counter.TextCounter(proj.spawner, f"Attack {target.name}: {dmg} damage{'s'*int(dmg>1)}!")
        else:
            counter.TextCounter(proj.spawner, f"Attack {target.name}: misses!")

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            weapon = user.equipment["main_hand"]
            base = user.DEX.mod
            num, dice = (1, 4)
            val, multi = weapon.critical
            speed = weapon.speed
            user.recoil += cls.recoil_cost * weapon.speed
            
            dmg = max(1, roll(num, dice) + base)
            crit = (val, max(1, multi*roll(num, dice) + base))
            entity.Arrow(_spawner = user, _max_range=weapon.range, _on_hit=cls.hit, _dmg=dmg, _crit=crit)


class FireBall(Action):
    name = "fire"
    recoil_cost = MAX_RECOIL
    description = "Just cast fireball"
    MP_cost = 2

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and user.location.is_empty(user.forward)

    @classmethod
    def hit(cls, proj):
        num, dice = (proj.fragment, 6)
        base = 0
        target = proj.location.get(proj.forward)
        if target:
            dmg = max(1, roll(num, dice) + base)
            target.hit(dmg)
            if target.is_dead:
                proj.spawner.exp += EXP_PER_KILL
            counter.TextCounter(proj.spawner, f"FIREBALL in {target.name}\'s face: {dmg} damage{'s'*int(dmg>1)}!")
        
        if proj.fragment > 1:
            px, py, pz = proj.position
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
            user.MP += cls.MP_cost

class IceWall(Action):
    name = "ice-wall"
    recoil_cost = MAX_RECOIL
    description = "Wall of Ice"
    MP_cost = 1

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            for t in range(max(1, user.INT.mod+1)):
                d = 2
                x, y, z = user.forward
                delta_x = int(user.direction=="down") - int(user.direction=="up")
                delta_y = int(user.direction=="right") - int(user.direction=="left")
                pos = (x + d*delta_x + t*delta_y, y + d*delta_y + t*delta_x, z)
                if user.location.is_empty(pos):
                    w = entity.IceWall(_spawner = user, _position=pos, _location=user.location)
                pos = (x + d*delta_x - t*delta_y, y + d*delta_y - t*delta_x, z)
                if user.location.is_empty(pos):
                    w = entity.IceWall(_spawner = user, _position=pos, _location=user.location)
            user.recoil += cls.recoil_cost
            user.MP += cls.MP_cost

class Teleport(Action):
    name = "teleport"
    recoil_cost = MAX_RECOIL
    MP_cost = 1
    description = "Teleport"

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            x, y, z = user.position
            new_pos = user.location.free_position(user)
            if new_pos:
                user.position = new_pos
                user.recoil += cls.recoil_cost
                user.MP += cls.MP_cost

class Hide(Action):
    name = "hide"
    recoil_cost = MIN_RECOIL
    description = "Hide in shadows"

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        return super().requisites(user) and not "hide" in user.counters and not user.equipment["body"]

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            counter.HideCounter(user, MAX_RECOIL)
            user.recoil += MED_RECOIL
            counter.TextCounter(user, f"{user.name} hides in shadows")
        elif "hide" in user.counters:
            user.counters["hide"].on_end()
            

class Trap(Action):
    name = "trap"
    recoil_cost = LONG_RECOIL
    description = "Set trap"

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        x, y, z = user.position
        return super().requisites(user) and user.location.is_empty((x, y, 0))

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            x, y, z = user.position
            trap = entity.Trap(_spawner = user, _on_hit=cls.hit, _location=user.location, _position=(x, y, 0))
            user.recoil += cls.recoil_cost

    @classmethod
    def hit(cls, trap):
        num, dice = (1, 4)
        base = trap.spawner.INT.mod
        target = trap.location.get(trap.above)
        if not isinstance(target, character.Character):
            return
        
        dmg = max(1, roll(num, dice) + base)
        target.hit(dmg)
        if target.is_dead:
            trap.spawner.exp += EXP_PER_KILL
        counter.TextCounter(target, f"{target.name} triggered a trap: {dmg} damage{'s'*int(dmg>1)}!")
        

class Sing(Action):
    name = "sing"
    recoil_cost = MED_RECOIL
    description = "Sing2Buff"
    SONG_LENGTH = 10

    # @classmethod
    # def requisites(cls, user):
    #     """Defines action legality"""
    #     return super().requisites(user) and "sing" not in user.counters

    @classmethod
    def hit(cls, song):
        base = song.spawner.CHA.mod
        target = song.location.get(song.below)
        counter.TextCounter(target, f"{song.spawner.name}\'s song! STR +{base}")
        counter.BuffCounter(target, cls.SONG_LENGTH + song.spawner.CHA.mod, "STR", max(1, song.spawner.CHA.mod))

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            user.recoil += cls.recoil_cost
            counter.TextCounter(user, f"Start singing")
            counter.SingCounter(user, MAX_RECOIL, cls.hit)
            
        elif "sing" in user.counters:
            user.counters["sing"].on_end()

class Charge(Action):
    name = "charge"
    recoil_cost = SHORT_RECOIL
    description = "Charge!!"                

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        weapon = user.equipment["main_hand"]
        return super().requisites(user) and "charge" not in user.counters and not isinstance(weapon, item.Bow)

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            dash = {"right":DashRight, "left":DashLeft, "up":DashUp, "down":DashDown}[user.direction].use
            attack = Attack.hit
            counter.ChargeCounter(user, MAX_RECOIL, dash, attack)
            counter.TextCounter(user, f"CHAAAAARGE!")

class Summon(Action):
    name = "summon"
    recoil_cost = LONG_RECOIL
    description = "Summon monster"
    MP_cost = 2

    @classmethod
    def requisites(cls, user):
        """Defines action legality"""
        x, y, z = user.position
        return super().requisites(user) and user.location.is_empty((x, y, 0))

    @classmethod
    def summon(cls, user):
        if user.CHA.mod >= 3:
            return bestiary.goblin
        else:
            return bestiary.goblin

    @classmethod
    def use(cls, user):
        if cls.requisites(user):
            counter.TextCounter(user, f"Starts a summon ritual")
            x, y, z = user.position
            entity.SummonPortal(_spawner=user, _summon=cls.summon(user), _location=user.location, _position=(x, y, 0))
            user.recoil += cls.recoil_cost
            user.MP += cls.MP_cost


