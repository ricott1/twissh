from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from typing import Callable

import esper
from hacknslassh.components.characteristics import RGB

from hacknslassh.components.description import ActorInfo, Size
from hacknslassh.components.image import ImageLayer
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User
from hacknslassh.components.utils import DelayCallback, ParryCallback
from .base import Component

class EquipmentSlot(str, Enum):
    HEAD = "head"
    BODY = "body"
    LEGS = "legs"
    FEET = "feet"
    BELT = "belt"
    WEAPON = "weapon"

@dataclass
class EquippableItem(Component):
    slot: EquipmentSlot
    size: Size
    requisites: Callable[[esper.World, int], None] | None = None

    def __post_init__(self) -> None:
        if self.slot == EquipmentSlot.HEAD:
            self.image_layer = ImageLayer.HEAD_EQUIPMENT
        elif self.slot == EquipmentSlot.BODY:
            self.image_layer = ImageLayer.BODY_EQUIPMENT
        elif self.slot == EquipmentSlot.LEGS:
            self.image_layer = ImageLayer.LEGS_EQUIPMENT
        elif self.slot == EquipmentSlot.FEET:
            self.image_layer = ImageLayer.FEET_EQUIPMENT
        elif self.slot == EquipmentSlot.WEAPON:
            self.image_layer = ImageLayer.WEAPON
        elif self.slot == EquipmentSlot.BELT:
            self.image_layer = ImageLayer.BELT_EQUIPMENT
        else:
            raise ValueError(f"Invalid slot {self.slot}")

    @classmethod
    def head(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.HEAD, size)
    
    @classmethod
    def body(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.BODY, size)
    
    @classmethod
    def legs(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.LEGS, size)
    
    @classmethod
    def shoes(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.SHOES, size)
    
    @classmethod
    def belt(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.BELT, size)
    
    @classmethod
    def weapon(cls, size: Size) -> EquippableItem:
        return cls(EquipmentSlot.WEAPON, size)


@dataclass
class RangeWeapon(Component):
    pass

@dataclass
class MeleeWeapon(Component):
    pass

@dataclass
class Projectile(Component):
    spawner_id: int
    origin: tuple[int, int, int]
    velocity: int = 1
    range: int = 6

    def on_hit(self, world: esper.World, entity_id: int, target_id: int) -> None:
        target_info = world.try_component(target_id, ActorInfo)
        print(f"Projectile {entity_id} hit {target_id}")
        if not target_info:
            return
        
        print(f"Target is {target_info.name}")
        in_location = world.try_component(entity_id, InLocation)
        target_in_location = world.try_component(target_id, InLocation)
        parry = world.try_component(target_id, ParryCallback)

        if parry and in_location and in_location.forward == target_in_location.position and target_in_location.forward == in_location.position:
            parry.delay = 0
            message = f"{target_info.name} parried!"
        else:
            dmg = 15
            target_rgb = world.try_component(target_id, RGB) 
            target_rgb.red.value -= dmg
            message = f"Attack {target_info.name}: {dmg} damages!"
            world.add_component(target_id, DelayCallback.colorPulse(world, target_id))
            if target_user := world.try_component(target_id, User):
                target_user.mind.process_event("player_rgb_changed")
        
        if user := world.try_component(self.spawner_id, User):
            user.mind.process_event("log", ("green", message))
            user.mind.process_event("player_acting_changed")
        
        
        for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
            if other_ent_id != self.spawner_id and other_in_loc.dungeon == in_location.dungeon and in_location.position in other_sight.visible_tiles:
                other_user.mind.process_event("redraw_ui")


@dataclass
class Equipment(Component):
    """
    The equipment held by the entity.
    """
    head: int | None = None
    body: int | None = None
    legs: int | None = None
    shoes: int | None = None
    belt: int | None = None
    weapon: int | None = None
    
    def add(self, slot: EquipmentSlot, entity: int) -> None:
        setattr(self, slot.value, entity)

    def remove(self, slot: EquipmentSlot) -> None:
        setattr(self, slot.value, None)
    
    def get_bonus(self, bonus: str) -> int:
        bonus = 0
        for slot in EquipmentSlot:
            item = getattr(self, slot.value)
            if item is not None:
                bonus += getattr(item, bonus, 0)
        return bonus
    
    def get_item(self, slot: EquipmentSlot) -> int | None:
        return getattr(self, slot.value)
    