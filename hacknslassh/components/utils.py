from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import esper
from hacknslassh.color_utils import Color

from hacknslassh.components.base import Component
from hacknslassh.components.in_location import ActiveMarkers, InLocation
from hacknslassh.components.sight import Sight
from hacknslassh.components.user import User

@dataclass
class DelayCallback(Component):
    """
    Component for delaying a callback.
    """

    callback: Callable
    delay: float

    @classmethod
    def colorPulse(cls, world: esper.World, ent_id: int, color: Color = Color.RED) -> DelayCallback:
        def callback(w: esper.World, e: int) -> None:
            if in_loc := w.try_component(e, InLocation):
                if in_loc.fg == color:
                    in_loc.fg = original_fg
                    in_loc.dungeon.set_renderable_entity(e)
                    if user := world.try_component(ent_id, User):
                        user.mind.process_event("redraw_ui")
                    for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
                        if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and in_loc.position in other_sight.visible_tiles:
                            other_user.mind.process_event("redraw_ui")

        in_loc = world.component_for_entity(ent_id, InLocation)
        original_fg = in_loc.fg
        in_loc.fg = color
        in_loc.dungeon.set_renderable_entity(ent_id)
        return DelayCallback(callback, 0.25)
    
    @classmethod
    def markerPulse(cls, world: esper.World, ent_id: int, markers: ActiveMarkers) -> DelayCallback:
        def callback(w: esper.World, e: int) -> None:
            if in_loc := w.try_component(e, InLocation):
                if in_loc.active_markers == markers:
                    in_loc.active_markers = original_markers
                    in_loc.dungeon.set_renderable_entity(e)#FIXME: do this automatically
                    if user := world.try_component(ent_id, User):
                        user.mind.process_event("redraw_ui")
                    for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
                        if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and in_loc.position in other_sight.visible_tiles:
                            other_user.mind.process_event("redraw_ui")

        in_loc = world.component_for_entity(ent_id, InLocation)
        original_markers = in_loc.active_markers
        in_loc.active_markers = markers
        in_loc.dungeon.set_renderable_entity(ent_id)
        return DelayCallback(callback, 0.25)

@dataclass
class ParryCallback(DelayCallback):

    @classmethod
    def new(cls, world: esper.World, ent_id: int, delay: float) -> DelayCallback:
        def callback(w: esper.World, e: int) -> None:
            if in_loc := w.try_component(e, InLocation):
                if in_loc.active_markers == ActiveMarkers.PARRY:
                    in_loc.active_markers = original_markers
                    in_loc.dungeon.set_renderable_entity(e)#FIXME: do this automatically
                    if user := world.try_component(ent_id, User):
                        user.mind.process_event("redraw_ui")
                    for other_ent_id, (other_user, other_in_loc, other_sight) in world.get_components(User, InLocation, Sight):
                        if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and in_loc.position in other_sight.visible_tiles:
                            other_user.mind.process_event("redraw_ui")

        in_loc = world.component_for_entity(ent_id, InLocation)
        original_markers = in_loc.active_markers
        in_loc.active_markers = ActiveMarkers.PARRY
        in_loc.dungeon.set_renderable_entity(ent_id)
        return ParryCallback(callback, delay)


@dataclass
class DeathCallback(Component):
    """
    Component for delaying a callback.
    """

    delay = 600
