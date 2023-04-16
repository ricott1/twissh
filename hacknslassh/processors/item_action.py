from __future__ import annotations
import esper
from hacknslassh.components.description import ActorInfo
from hacknslassh.components.equipment import Equipment, EquippableItem
from hacknslassh.components.item import ConsumableItem, ItemInfo, QuickItemSlots, QuickItems
from hacknslassh.components.sight import MAX_SIGHT_RADIUS, Sight
from hacknslassh.components.tokens import CatchableToken
from hacknslassh.components.user import User
from hacknslassh.components.acting import Acting
from hacknslassh.processors.action import Action

from ..components.in_location import Direction, InLocation
from hacknslassh.constants import *

class PickUp(Action):
    name = "pick up"
    recoil_cost = Recoil.SHORT
    description = "Pick up an item"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        user: User = world.try_component(ent_id, User)
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        dungeon = in_location.dungeon
        target_id = dungeon.get_at(in_location.forward_below)
        if not target_id:
            return
        consumable_item = world.try_component(target_id, ConsumableItem)
        equippable_item = world.try_component(target_id, EquippableItem)
        if not consumable_item and not equippable_item:
            return
        
        target_info = world.component_for_entity(target_id, ItemInfo)
        player_equipment: Equipment = world.try_component(ent_id, Equipment)
        
        if consumable_item:
            #check if the user has free quick item slots, else return and log can't pick up
            player_quick_items = world.component_for_entity(ent_id, QuickItems)
            num_slots = QuickItemSlots.BASE_SLOTS
            if player_equipment and player_equipment.belt and hasattr(player_equipment.belt, "slots"):
                num_slots += player_equipment.belt.slots
            for i in range(1, num_slots + 1):
                if i not in player_quick_items.slots or not player_quick_items.slots[i]:
                    player_quick_items.slots[i] = target_id
                    if user:
                        user.mind.process_event("player_added_quick_item", i)
                    break
            else:
                if user:
                    user.mind.process_event("log", ("red", f"Can\'t pick up {target_info.description}: no slot available."))
                return

        elif equippable_item:
            #check if the user has free equipment slots, else return and log can't pick up
            if not getattr(player_equipment, equippable_item.slot.value):
                setattr(player_equipment, equippable_item.slot.value, target_id)
                user.mind.process_event("player_equipment_changed")
            else:
                if user:
                    user.mind.process_event("log", ("red", f"Can\'t equip {target_info.description}: slot already equipped."))
                return
            
        acting.action_recoil = cls.recoil_cost

        in_location.dungeon.remove_renderable_entity_at(in_location.forward_below)
        target_in_location = world.component_for_entity(target_id, InLocation)
        # world.remove_component(target, InLocation)
        target_in_location.dungeon = None
        
        if user:
            info = world.component_for_entity(ent_id, ActorInfo)
            user.mind.process_event("log", ("green", f"{info.name} picked up {target_info.description.lower()}."))
            user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")

class Drop(Action):
    name = "drop"
    recoil_cost = Recoil.MINIMUM
    description = "Drop an item"
    slot = None

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        user: User = world.try_component(ent_id, User)
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        dungeon = in_location.dungeon
        
        player_quick_items = world.component_for_entity(ent_id, QuickItems)
        if cls.slot not in player_quick_items.slots or not player_quick_items.slots[cls.slot]:
            if user:
                user.mind.process_event("log", ("red", f"Nothing to drop on {cls.slot}."))
            return
        
        if dungeon.get_at(in_location.below):
            if user:
                user.mind.process_event("log", ("red", f"Can\'t drop here."))
            return
        
        
        acting.action_recoil = cls.recoil_cost
        
        target_id = player_quick_items.slots[cls.slot]
        target_in_location = world.component_for_entity(target_id, InLocation)
        target_in_location.dungeon = in_location.dungeon
        target_in_location.position = in_location.below
        in_location.dungeon.set_renderable_entity(target_id)
        player_quick_items.slots[cls.slot] = None
        
        if user:
            info = world.component_for_entity(ent_id, ActorInfo)
            target_info = world.component_for_entity(target_id, ItemInfo)
            user.mind.process_event("log", ("green", f"{info.name} dropped {target_info.description.lower()}."))
            user.mind.process_event("player_removed_quick_item", cls.slot)
            user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")

class Drop1(Drop):
    slot = 1

class Drop2(Drop):
    slot = 2

class Drop3(Drop):
    slot = 3

class Drop4(Drop):
    slot = 4

class Drop5(Drop):
    slot = 5

class Use(Action):
    name = "use"
    recoil_cost = Recoil.MINIMUM
    description = "Use an item"
    slot = None

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        user: User = world.try_component(ent_id, User)
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        
        in_location = world.component_for_entity(ent_id, InLocation)
        dungeon = in_location.dungeon
        
        player_quick_items = world.component_for_entity(ent_id, QuickItems)
        if cls.slot not in player_quick_items.slots or not player_quick_items.slots[cls.slot]:
            if user:
                user.mind.process_event("log", ("red", f"Nothing to use on {cls.slot}."))
            return
        
        
        acting.action_recoil = cls.recoil_cost
        
        target_id = player_quick_items.slots[cls.slot]
        if consumable := world.try_component(target_id, ConsumableItem):
            consumable.effect(world, ent_id)
        
        
        player_quick_items.slots[cls.slot] = None
        
        if user:
            info = world.component_for_entity(ent_id, ActorInfo)
            target_info = world.component_for_entity(target_id, ItemInfo)
            user.mind.process_event("log", ("green", f"{info.name} used {target_info.description.lower()}."))
            user.mind.process_event("player_removed_quick_item", cls.slot)
            user.mind.process_event("redraw_ui")
            user.mind.process_event("player_acting_changed")
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != ent_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")
        
        world.delete_entity(target_id)

class Use1(Use):
    slot = 1

class Use2(Use):
    slot = 2

class Use3(Use):
    slot = 3

class Use4(Use):
    slot = 4

class Use5(Use):
    slot = 5