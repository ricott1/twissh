import esper
from hacknslassh.components.acting import Acting

from hacknslassh.components.characteristics import RGB
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.tokens import IncreasedSightToken
from hacknslassh.components.user import User
from hacknslassh.constants import Recoil
from hacknslassh.processors.action import Action
from hacknslassh.components.sight import Sight, SightShape, MAX_SIGHT_RADIUS


class ChangeSightShape(Action):
    name = "change_sight_shape"
    recoil_cost = Recoil.SHORT
    green_cost = 2
    description = "Change sight shape"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        green = world.component_for_entity(ent_id, RGB).green
        if green.value < cls.green_cost:
            return
        green.value -= cls.green_cost
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        acting.action_recoil = cls.recoil_cost
        sight = world.component_for_entity(ent_id, Sight)
        # if sight.shape == SightShape.CIRCLE:
        #     sight.shape = SightShape.SQUARE
        if sight.shape == SightShape.CIRCLE:
            sight.shape = SightShape.CONE
        elif sight.shape == SightShape.CONE:
            sight.shape = SightShape.CIRCLE

        in_location = world.component_for_entity(ent_id, InLocation)
        x0, y0, _ = in_location.position
        sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
        
        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_green_changed")
            user.mind.process_event("player_status_changed")
            user.mind.process_event("redraw_local_ui")


class IncreaseSightRadius(Action):
    name = "increase_sight.radius"
    recoil_cost = Recoil.SHORT
    blue_cost = 5
    description = "Increase sight radius"
    duration = 3

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        sight = world.component_for_entity(ent_id, Sight)
        
        if sight.radius == MAX_SIGHT_RADIUS:
            return
        blue = world.component_for_entity(ent_id, RGB).blue
        if blue.value < cls.blue_cost:
            return
        blue.value -= cls.blue_cost
        
        increasead_sight_radius: IncreasedSightToken = world.try_component(ent_id, IncreasedSightToken)
        if not increasead_sight_radius:
            world.add_component(ent_id, IncreasedSightToken([cls.duration]))
        else:
            increasead_sight_radius.values.append(cls.duration)
        sight.radius += 1

        in_location = world.component_for_entity(ent_id, InLocation)
        x0, y0, _ = in_location.position
        sight.update_visible_and_visited_tiles((x0, y0), in_location.direction, in_location.dungeon)
        
        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_blue_changed")
            user.mind.process_event("player_status_changed")
            user.mind.process_event("redraw_local_ui")
