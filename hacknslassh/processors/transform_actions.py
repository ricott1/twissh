from dataclasses import dataclass
import random
from hacknslassh.color_utils import Color
from hacknslassh.components.acting import Acting
from hacknslassh.components.base import Component
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.rarity import Rarity
from hacknslassh.components.sight import Sight, SightShape
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.image import Image, ImageCollection, ImageTransition
from hacknslassh.components.description import ID, ActorInfo, GameClassName, Language
from hacknslassh.components.tokens import TransformedToken
from hacknslassh.components.user import User
from hacknslassh.components.utils import DelayCallback
from hacknslassh.constants import Recoil
from hacknslassh.processors.action import Action

from hacknslassh.processors.image_composer import random_image_from_game_class

import esper

class TransformingToken(DelayCallback):
    pass


class TransformInto(Action):
    name = "transform_to_"
    recoil_cost = Recoil.MAX
    description = "Transform into"
    red_mod = 0
    green_mod = 0
    blue_mod = 0
    extra_components = {}

    @classmethod
    def target(cls, world: esper.World, ent_id: int) -> ActorInfo:
        _from: ActorInfo = world.component_for_entity(ent_id, ActorInfo) 
        return _from

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        
        if world.try_component(ent_id, TransformingToken):
            return
        
        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return

        transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
        # print("transformed_token", transformed_token)
         
        if not transformed_token:

            rgb: RGB = world.component_for_entity(ent_id, RGB)
            # print("rgb", rgb.red.value, rgb.green.value, rgb.blue.value)
            # print("cost", cls.red_mod, cls.green_mod, cls.blue_mod)
            if (rgb.red.value == 0 and  cls.red_mod < 0) or (rgb.green.value == 0 and cls.green_mod < 0) or (rgb.blue.value == 0 and cls.blue_mod < 0):
                return
        
        if not transformed_token:  
            _into = cls.target(world, ent_id)
        elif transformed_token:
            _into = transformed_token._from

        _id = world.component_for_entity(ent_id, ID).uuid
        new_surface = random_image_from_game_class(_into.game_class, _into.gender.value.to_bytes() + _id).surface
        acting.action_recoil = cls.recoil_cost
        
        old_surface = world.component_for_entity(ent_id, Image).surface
        img_transition = ImageTransition(old_surface, new_surface, cls.recoil_cost)
        world.add_component(ent_id, img_transition)
        world.add_component(ent_id, TransformingToken(lambda w, ent_id: cls.transform(w, ent_id, _into), img_transition.delay))
        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_acting_changed")
            info = world.component_for_entity(ent_id, ActorInfo)
            user.mind.process_event("log", ("cyan", f"{info.name} is transforming into {_into.description.lower()}"))
        
    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: ActorInfo) -> None:
        transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken) 
        if transformed_token:
            world.remove_component(ent_id, TransformedToken)
            world.add_component(ent_id, transformed_token._from)
            for _, comp in transformed_token.extra_components.items():
                world.add_component(ent_id, comp)
        else:
            extra_components = {}
            for k, (comp_type, comp) in cls.extra_components.items():
                old_comp = world.component_for_entity(ent_id, comp_type)
                extra_components[k] = old_comp
                new_comp = comp_type.merge(old_comp, comp)
                world.add_component(ent_id, new_comp, comp_type)
            _from: ActorInfo = world.component_for_entity(ent_id, ActorInfo)
            transformed_token = TransformedToken(_from, _into, extra_components, cls.on_processor)
            world.add_component(ent_id, transformed_token)
            world.add_component(ent_id, _into)

        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_status_changed")
            user.mind.process_event("redraw_ui")
    
    @classmethod
    def on_processor(cls, world: esper.World, ent_id: int, dt: float) -> None:
        rgb: RGB = world.component_for_entity(ent_id, RGB)
        blue_int = int(rgb.blue.value)
        rgb.blue._value += cls.blue_mod * dt
        if user := world.try_component(ent_id, User):
            if blue_int != int(rgb.blue.value):
                user.mind.process_event("player_rgb_changed")

        green_int = int(rgb.green.value)
        rgb.green._value += cls.green_mod * dt
        if user := world.try_component(ent_id, User):
            if green_int != int(rgb.green.value):
                user.mind.process_event("player_rgb_changed")
        
        red_int = int(rgb.red.value)
        rgb.red._value += cls.red_mod * dt
        if user := world.try_component(ent_id, User):
            if red_int != int(rgb.red.value):
                user.mind.process_event("player_rgb_changed")

        if rgb.blue.value <= 0 or rgb.green.value <= 0 or rgb.red.value <= 0:
            transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
            if not transformed_token:
                return
            
            if not world.try_component(ent_id, TransformingToken):
                _id = world.component_for_entity(ent_id, ID).uuid
                new_surface = random_image_from_game_class(transformed_token._from.game_class, transformed_token._from.gender.value.to_bytes() + _id).surface
                old_surface = world.component_for_entity(ent_id, Image).surface
                world.add_component(ent_id, ImageTransition(old_surface, new_surface, cls.recoil_cost))
            else:
                world.remove_component(ent_id, TransformingToken)

            acting = world.try_component(ent_id, Acting)
            acting.action_recoil = max(acting.action_recoil, cls.recoil_cost)
            cls.transform(world, ent_id, transformed_token._from)

@dataclass
class DevilInfo(ActorInfo):
    description = "A serious devil"
    game_class = GameClassName.DEVIL

@dataclass
class DwarvilInfo(ActorInfo):
    description = "A serious, small devil"
    game_class = GameClassName.DWARVIL

class TransformIntoDevil(TransformInto):
    name = "transform_to_devil"
    description = "Transform into a devil"
    red_mod = 5
    green_mod = -5
    blue_mod = -5

    @classmethod
    def target(cls, world: esper.World, ent_id: int) -> ActorInfo:
        _from: ActorInfo = world.component_for_entity(ent_id, ActorInfo)
        if _from.game_class == GameClassName.DWARF:
            return ActorInfo.merge(_from, DwarvilInfo) 
        return ActorInfo.merge(_from, DevilInfo)
    
@dataclass
class CatInfo(ActorInfo):
    description = "A serious cat."
    game_class = GameClassName.CAT
    languages = [Language.GATTESE, Language.COMMON]

@dataclass
class CatSight(Sight):
    shape = SightShape.CIRCLE

class TransformIntoCat(TransformInto):
    name = "transform_to_cat"
    red_mod = 0
    green_mod = 0.25
    blue_mod = -0.5
    description = "Transform into a cat"
    extra_components = {"sight": (Sight, CatSight)}

    @classmethod
    def target(cls, world: esper.World, ent_id: int) -> ActorInfo:
        _from: ActorInfo = world.component_for_entity(ent_id, ActorInfo)
        return ActorInfo.merge(_from, CatInfo)

    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: ActorInfo) -> None:
        old_sight: Sight = world.component_for_entity(ent_id, Sight)
        super().transform(world, ent_id, _into)
        new_sight = world.component_for_entity(ent_id, Sight)
        new_sight.visited_tiles.update(old_sight.visited_tiles)

        in_location: InLocation = world.component_for_entity(ent_id, InLocation)
        rarity = Rarity.common()
        in_location.fg = rarity.color

        if user := world.try_component(ent_id, User):
            user.mind.process_event("redraw_ui")
    
    @classmethod
    def on_processor(cls, world: esper.World, ent_id: int, dt: float) -> None:
        super().on_processor(world, ent_id, dt)
        in_location: InLocation = world.component_for_entity(ent_id, InLocation)
        # reset fg to default
        in_location.fg = Color.WHITE
        if user := world.try_component(ent_id, User):
            user.mind.process_event("redraw_ui")


class TransformIntoRandom(TransformInto):
    name = "transform_to_random"
    description = "Transform"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        target_cls = random.choice([TransformIntoCat, TransformIntoCat])
        target_cls.use(world, ent_id)
