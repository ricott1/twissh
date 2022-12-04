from hacknslassh.components.acting import Acting
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.sight import Sight
from hacknslassh.components.characteristics import RGB
from hacknslassh.components.image import Image, ImageCollection, ImageTransition
from hacknslassh.components.description import CatInfo, DevilInfo, DwarvilInfo, Info, GameClassName
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
    recoil_cost = Recoil.MEDIUM
    description = "Transform into"

    @classmethod
    def use(cls, world: esper.World, ent_id: int, _into: Info) -> None:

        if world.try_component(ent_id, TransformingToken):
            return

        transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
        
        if not transformed_token:  
            new_surface = ImageCollection.CHARACTERS[_into.gender][_into.game_class].surface
        elif transformed_token and transformed_token._into == _into:
            new_surface = ImageCollection.CHARACTERS[transformed_token._from.gender][transformed_token._from.game_class].surface
        else:
            return

        acting = world.try_component(ent_id, Acting)
        if not acting or acting.action_recoil > 0:
            return
        acting.action_recoil = cls.recoil_cost
        
        old_surface = world.component_for_entity(ent_id, Image).surface
        img_transition = ImageTransition(old_surface, new_surface)
        world.add_component(ent_id, img_transition)
        world.add_component(ent_id, TransformingToken(lambda w, ent_id: cls.transform(w, ent_id, _into), img_transition.delay//2))
        
    
    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: Info) -> None:
        transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
        _from: Info = world.component_for_entity(ent_id, Info)

        if transformed_token:
            world.remove_component(ent_id, TransformedToken)
            world.add_component(ent_id, transformed_token._from)
        else:
            transformed_token = TransformedToken(_from, _into, {}, cls.on_processor)
            world.add_component(ent_id, transformed_token)
            world.add_component(ent_id, _into)

        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_status_changed")
    
    @classmethod
    def on_processor(cls, world: esper.World, ent_id: int, dt: float) -> None:
        pass

class TransformIntoDevil(TransformInto):
    name = "transform_to_devil"
    recoil_cost = Recoil.MEDIUM
    cost = 0.75
    description = "Transform into a devil"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        _from: Info = world.component_for_entity(ent_id, Info)
        if _from.game_class == GameClassName.DWARF:
            _into = Info.merge_info(_from, DwarvilInfo) 
        else:
            _into = Info.merge_info(_from, DevilInfo)
        super().use(world, ent_id, _into)
    
        
class TransformIntoCat(TransformInto):
    name = "transform_to_cat"
    recoil_cost = Recoil.MEDIUM
    cost = 0.5
    description = "Transform into a cat"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        rgb: RGB = world.component_for_entity(ent_id, RGB)
        if rgb.blue.value < cls.cost:
            return
        _into = Info.merge_info(world.component_for_entity(ent_id, Info), CatInfo)
        super().use(world, ent_id, _into)

    @classmethod
    def transform(cls, world: esper.World, ent_id: int, _into: Info) -> None:
        transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
        
        if transformed_token:
            world.remove_component(ent_id, TransformedToken)
            world.add_component(ent_id, transformed_token._from)
            old_sight = world.component_for_entity(ent_id, Sight)
            new_sight = transformed_token.extra_components["sight"]
            new_sight.visited_tiles.update(old_sight.visited_tiles)
            world.add_component(ent_id, new_sight)
        else:
            _from: Info = world.component_for_entity(ent_id, Info)
            old_sight = world.component_for_entity(ent_id, Sight)
            new_sight = Sight.cat_sight()
            new_sight.visited_tiles.update(old_sight.visited_tiles)
            extra_components = {"sight": old_sight}
            transformed_token = TransformedToken(_from, _into, extra_components, cls.on_processor)
            world.add_component(ent_id, transformed_token)
            world.add_component(ent_id, _into)
            world.add_component(ent_id, new_sight)
            
        in_loc = world.component_for_entity(ent_id, InLocation)
        x, y, _ = in_loc.position
        world.component_for_entity(ent_id, Sight).update_visible_and_visited_tiles((x, y), in_loc.direction, in_loc.dungeon)

        if user := world.try_component(ent_id, User):
            user.mind.process_event("player_status_changed")
    
    @classmethod
    def on_processor(cls, world: esper.World, ent_id: int, dt: float) -> None:
        rgb: RGB = world.component_for_entity(ent_id, RGB)
        blue_int = int(rgb.blue.value)
        rgb.blue._value -= cls.cost * dt
        if user := world.try_component(ent_id, User):
            if blue_int != int(rgb.blue.value):
                user.mind.process_event("player_blue_changed")

        green_int = int(rgb.blue.value)
        rgb.green._value += 0.5 * cls.cost * dt
        if user := world.try_component(ent_id, User):
            if green_int != int(rgb.green.value):
                user.mind.process_event("player_green_changed")

        if rgb.blue.value <= 0:
            transformed_token: TransformedToken = world.try_component(ent_id, TransformedToken)
            if not transformed_token:
                return
            
            if not world.try_component(ent_id, TransformingToken):
                new_surface = ImageCollection.CHARACTERS[transformed_token._from.gender][transformed_token._from.game_class].surface
                old_surface = world.component_for_entity(ent_id, Image).surface
                world.add_component(ent_id, ImageTransition(old_surface, new_surface))
            else:
                world.remove_component(ent_id, TransformingToken)

            cls.transform(world, ent_id, transformed_token._from)

    