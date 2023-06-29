from __future__ import annotations
import esper
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.description import ActorInfo
from hacknslassh.components.equipment import RangeWeapon, Equipment
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.components.utils import DelayCallback, ParryCallback
from hacknslassh.factories.arrow_factory import create_arrow
from hacknslassh.processors.action import Action
from hacknslassh.utils import distance
from hacknslassh.components.in_location import InLocation, ActiveMarkers
from hacknslassh.constants import *

class Attack(Action):
    name = "attack"
    recoil_cost = Recoil.MEDIUM
    description = "Attack"
    range = 1

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return

        equipment = world.try_component(ent_id, Equipment)
        if equipment and equipment.weapon and world.has_component(equipment.weapon, RangeWeapon):
            cls.range_attack(world, ent_id)
        else:
            cls.melee_attack(world, ent_id)
    
    @classmethod
    def range_attack(cls, world: esper.World, ent_id: int) -> None:
        acting = world.try_component(ent_id, Acting)
        in_location = world.component_for_entity(ent_id, InLocation)
        print(in_location.forward,  in_location.dungeon.is_empty_at(in_location.forward))
        if in_location.dungeon.is_empty_at(in_location.forward):
            arrow_id = world.create_entity(*create_arrow(ent_id, in_location))
            in_location.dungeon.set_renderable_entity(arrow_id)
        
            acting.action_recoil = cls.recoil_cost
            world.add_component(ent_id, DelayCallback.markerPulse(world, ent_id, ActiveMarkers.ATTACK))
            if user := world.try_component(ent_id, User):
                user.mind.process_event("player_acting_changed")
            for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
                if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                    other_user.mind.process_event("redraw_ui")

    @classmethod
    def melee_attack(cls, world: esper.World, ent_id: int) -> None:
        acting = world.try_component(ent_id, Acting)
        target_id = acting.target
        if not target_id:
            return
        target_rgb = world.try_component(target_id, RGB) 
        if not target_rgb:
            return
        user = world.try_component(ent_id, User)   
        target_info = world.component_for_entity(target_id, ActorInfo)
        in_location = world.component_for_entity(ent_id, InLocation) 
        target_in_location = world.component_for_entity(target_id, InLocation)   
        if distance(in_location.position, target_in_location.position) > cls.range:
            if user:
                user.mind.process_event("log", ("red", f"Can\'t attack {target_info.name}: get closer!"))
            return
        
        world.add_component(ent_id, DelayCallback.markerPulse(world, ent_id, ActiveMarkers.ATTACK))
        parry = world.try_component(target_id, ParryCallback)

        if parry and in_location.forward == target_in_location.position and target_in_location.forward == in_location.position:
            parry.delay = 0
            message = f"{target_info.name} parried!"
        else:
            ent_rgb = world.component_for_entity(ent_id, RGB)
            dmg = 15 + (ent_rgb.red.value // 15) * random.randint(1, 5)
            target_rgb = world.try_component(target_id, RGB) 
            target_rgb.red.value -= dmg
            message = f"Attack {target_info.name}: {dmg} damages!"
            world.add_component(target_id, DelayCallback.colorPulse(world, target_id))
            if target_user := world.try_component(target_id, User):
                target_user.mind.process_event("player_rgb_changed")
        
        acting.action_recoil = cls.recoil_cost

        if user:
            user.mind.process_event("log", ("green", message))
            # user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
        
        
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
    