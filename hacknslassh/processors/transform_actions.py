from hacknslassh.components.characteristics import Mana
from hacknslassh.components.image import Image, ImageCollection, ImageTransition
from hacknslassh.components.description import Description, GameClassName
from hacknslassh.components.tokens import TransformedToken
from hacknslassh.components.user import User
from hacknslassh.constants import Recoil
from hacknslassh.processors.action import Action

import esper

class TransformToDevil(Action):
    name = "transform_to_devil"
    recoil_cost = Recoil.MEDIUM
    mana_cost = 2
    description = "Transform into a devil"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        mana = world.component_for_entity(ent_id, Mana)
        if mana.value < cls.mana_cost:
            return
        transformed_token = world.try_component(ent_id, TransformedToken)
        if transformed_token:
            if transformed_token.into == GameClassName.DEVIL:
                return
            world.remove_component(ent_id, TransformedToken)
        mana.value -= cls.mana_cost
        user = world.component_for_entity(ent_id, User)
        user.mind.process_event("player_mana_changed")
        info: Description = world.component_for_entity(ent_id, Description)
        old_surface = world.component_for_entity(ent_id, Image).surface
        

        if info.game_class == GameClassName.DWARF:
            new_surface = ImageCollection.CHARACTERS[info.gender][GameClassName.DWARVIL].surface
        else:
            new_surface = ImageCollection.CHARACTERS[info.gender][GameClassName.DEVIL].surface
        world.add_component(ent_id, ImageTransition(old_surface, new_surface))
        world.add_component(ent_id, TransformedToken(GameClassName.DEVIL))


class TransformToCat(Action):
    name = "transform_to_cat"
    recoil_cost = Recoil.MEDIUM
    mana_cost = 2
    description = "Transform into a cat"

    @classmethod
    def use(cls, world: esper.World, ent_id: int) -> None:
        mana = world.component_for_entity(ent_id, Mana)
        if mana.value < cls.mana_cost:
            return

        transformed_token = world.try_component(ent_id, TransformedToken)
        if transformed_token:
            if transformed_token.into == GameClassName.CAT:
                return
            world.remove_component(ent_id, TransformedToken)

        mana.value -= cls.mana_cost
        user = world.component_for_entity(ent_id, User)
        user.mind.process_event("player_mana_changed")
        info = world.component_for_entity(ent_id, Description)
        old_surface = world.component_for_entity(ent_id, Image).surface
        new_surface = ImageCollection.CHARACTERS[info.gender][GameClassName.CAT].surface
        world.add_component(ent_id, ImageTransition(old_surface, new_surface))
        world.add_component(ent_id, TransformedToken(GameClassName.CAT))
        
    