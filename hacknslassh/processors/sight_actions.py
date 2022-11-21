import esper

from hacknslassh.components.characteristics import Mana
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.tokens import IncreasedSightToken
from hacknslassh.components.user import User
from hacknslassh.constants import Recoil
from hacknslassh.processors.action import Action


class IncreaseSightRadius(Action):
    name = "increase_sight_radius"
    recoil_cost = Recoil.SHORT
    mana_cost = 1
    description = "Increase sight radius"
    duration = 3

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        in_location = world.component_for_entity(ent_id, InLocation)
        if in_location.sight_radius == in_location.MAX_SIGHT_RADIUS:
            return
        mana = world.component_for_entity(ent_id, Mana)
        if mana.value < cls.mana_cost:
            return
        mana.value -= cls.mana_cost
        
        increasead_sight_radius = world.try_component(ent_id, IncreasedSightToken)
        if not increasead_sight_radius:
            world.add_component(ent_id, IncreasedSightToken([cls.duration]))
        else:
            increasead_sight_radius.values.append(cls.duration)
        in_location.sight_radius += 1
        user = world.try_component(ent_id, User)
        if user:
            user.mind.process_event("player_mana_changed")
            user.mind.process_event("player_status_changed")
            user.mind.process_event("redraw_local_ui")
