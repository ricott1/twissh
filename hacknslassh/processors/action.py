from __future__ import annotations
import esper

from ..components.in_location import Direction, InLocation
from hacknslassh.constants import *

class Action(object):
    """implements rigid body properties"""

    name = ""
    recoil_cost = 0
    description = ""

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        """Use action"""
        pass

    @classmethod
    def target_square(cls, world: esper.World, ent_id: int) -> tuple[int, int, int] | None:
        """Get action target square"""
        in_location = world.try_component(ent_id, InLocation)
        if not in_location:
            return None
        return in_location.forward

    @classmethod
    def action_direction(cls, world: esper.World, ent_id: int) -> Direction:
        in_location = world.try_component(ent_id, InLocation)
        if not in_location:
            return None
        x, y, z = in_location.position
        xt, yt, zt = cls.target_square(world, ent_id)
        if (xt < x) and (yt == y):
            return Direction.DOWN
        elif (xt > x) and (yt == y):
            return Direction.UP
        elif (xt == x) and (yt < y):
            return Direction.RIGHT
        elif (xt == x) and (yt > y):
            return Direction.LEFT

    @classmethod
    def target(cls, world: esper.World, ent_id: int) -> int | None:
        """Get action target square"""
        in_location = world.try_component(ent_id, InLocation)
        if not in_location:
            return None
        target_square = cls.target_square(world, ent_id)
        if target_square:
            return in_location.dungeon.get_at(target_square)
        return None

    @classmethod
    def requisites(cls, world: esper.World, ent_id: int) -> bool:
        """Defines action legality"""
        return True

