from hacknslassh.components.characteristics import Mana
from hacknslassh.components.image import Image, ImageCollection, ImageTransition
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.info import Description, RaceType
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
        if world.has_component(ent_id, TransformedToken):
            return
        mana.value -= cls.mana_cost
        user = world.component_for_entity(ent_id, User)
        user.mind.process_event("player_mana_changed")
        info = world.component_for_entity(ent_id, Description)
        old_surface = world.component_for_entity(ent_id, Image).surface
        new_surface = ImageCollection.CHARACTERS[info.gender][RaceType.DEVIL].surface
        world.add_component(ent_id, ImageTransition(old_surface, new_surface))
        world.add_component(ent_id, TransformedToken())
        
        
    