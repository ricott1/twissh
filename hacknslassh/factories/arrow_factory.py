from __future__ import annotations
from hacknslassh.components.acting import Acting
from hacknslassh.components.base import Component
from hacknslassh.components.equipment import Projectile
from hacknslassh.components.in_location import Direction, InLocation
from hacknslassh.constants import Recoil


def create_arrow(spawner_id: int, ent_in_location: InLocation, should_store: bool = False) -> list[Component]:
    return [
        Projectile(spawner_id, ent_in_location.position),
        InLocation.Arrow(ent_in_location.dungeon, ent_in_location.forward, ent_in_location.direction),
        Acting(movement_recoil = Recoil.MINIMUM)
    ]
