from dataclasses import dataclass
import random
from hacknslassh.components.acting import Acting
from hacknslassh.components.base import Component
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.sight import Sight, SightShape
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.image import Image, ImageCollection, ImageTransition
from hacknslassh.components.description import Info, GameClassName, Language
from hacknslassh.components.tokens import TransformedToken
from hacknslassh.components.user import User
from hacknslassh.components.utils import DelayCallback
from hacknslassh.constants import Recoil
from hacknslassh.processors.action import Action

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
    def target(cls, world: esper.World, ent_id: int) -> Info:
        _from: Info = world.component_for_entity(ent_id, Info) 
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

        new_surface = ImageCollection.CHARACTERS[_into.gender][_into.game_class].surface
        acting.action_recoil = cls.recoil_cost
        
        old_surface = world.component_for_entity(ent_id, Image).surface
        img_transition = ImageTransition(old_surface, new_surface, cls.recoil_cost)
        world.add_component(ent_id, img_transition)
        world.add_component(ent_id, TransformingToken(lambda w, ent_id: cls.transform(w, ent_id, _into), img_transition.delay))
        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_acting_changed")
        
    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: Info) -> None:
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
            _from: Info = world.component_for_entity(ent_id, Info)
            transformed_token = TransformedToken(_from, _into, extra_components, cls.on_processor)
            world.add_component(ent_id, transformed_token)
            world.add_component(ent_id, _into)

        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_status_changed")
            user.mind.process_event("redraw_local_ui")
    
    @classmethod
    def on_processor(cls, world: esper.World, ent_id: int, dt: float) -> None:
        rgb: RGB = world.component_for_entity(ent_id, RGB)
        blue_int = int(rgb.blue.value)
        rgb.blue._value += cls.blue_mod * dt
        if user := world.try_component(ent_id, User):
            if blue_int != int(rgb.blue.value):
                user.mind.process_event("player_blue_changed")

        green_int = int(rgb.green.value)
        rgb.green._value += cls.green_mod * dt
        if user := world.try_component(ent_id, User):
            if green_int != int(rgb.green.value):
                user.mind.process_event("player_green_changed")
        
        red_int = int(rgb.red.value)
        rgb.red._value += cls.red_mod * dt
        if user := world.try_component(ent_id, User):
            if red_int != int(rgb.red.value):
                user.mind.process_event("player_red_changed")

        if rgb.blue.value <= 0 or rgb.green.value <= 0 or rgb.red.value <= 0:
            transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
            if not transformed_token:
                return
            
            if not world.try_component(ent_id, TransformingToken):
                new_surface = ImageCollection.CHARACTERS[transformed_token._from.gender][transformed_token._from.game_class].surface
                old_surface = world.component_for_entity(ent_id, Image).surface
                world.add_component(ent_id, ImageTransition(old_surface, new_surface, cls.recoil_cost))
            else:
                world.remove_component(ent_id, TransformingToken)

            acting = world.try_component(ent_id, Acting)
            acting.action_recoil = max(acting.action_recoil, cls.recoil_cost)
            cls.transform(world, ent_id, transformed_token._from)

@dataclass
class DevilInfo(Info):
    description = "A serious devil."
    game_class = GameClassName.DEVIL.value

@dataclass
class DwarvilInfo(Info):
    description = "A serious, small devil."
    game_class = GameClassName.DWARVIL.value

class TransformIntoDevil(TransformInto):
    name = "transform_to_devil"
    description = "Transform into a devil"
    red_mod = 5
    green_mod = -5
    blue_mod = -5

    @classmethod
    def target(cls, world: esper.World, ent_id: int) -> Info:
        _from: Info = world.component_for_entity(ent_id, Info)
        if _from.game_class == GameClassName.DWARF:
            return Info.merge(_from, DwarvilInfo) 
        return Info.merge(_from, DevilInfo)
    
@dataclass
class CatInfo(Info):
    description = "A serious cat."
    game_class = GameClassName.CAT.value
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
    def target(cls, world: esper.World, ent_id: int) -> Info:
        _from: Info = world.component_for_entity(ent_id, Info)
        return Info.merge(_from, CatInfo)

    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: Info) -> None:
        old_sight: Info = world.component_for_entity(ent_id, Sight)
        super().transform(world, ent_id, _into)
        new_sight = world.component_for_entity(ent_id, Sight)
        new_sight.visited_tiles.update(old_sight.visited_tiles)

        # in_loc = world.component_for_entity(ent_id, InLocation)
        # x, y, _ = in_loc.position
        # new_sight.update_visible_and_visited_tiles((x, y), in_loc.direction, in_loc.dungeon)

        if user := world.try_component(ent_id, User):
            user.mind.process_event("redraw_local_ui")


class TransformIntoRandom(TransformInto):
    name = "transform_to_random"
    description = "Transform"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        target_cls = random.choice([TransformIntoCat, TransformIntoCat])
        target_cls.use(world, ent_id)
