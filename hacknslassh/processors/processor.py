import esper
from hacknslassh.components.acting import Ai
from hacknslassh.components.equipment import Projectile
from hacknslassh.components.tokens import IncreasedSightToken, TransformedToken
from hacknslassh.color_utils import Color
from hacknslassh.components.utils import ParryCallback
from hacknslassh.constants import Recoil
from hacknslassh.dungeon import Dungeon
from hacknslassh.processors.move_actions import MoveDown, MoveLeft, MoveRight, MoveUp
from hacknslassh.processors.target_action import Target
from hacknslassh.processors.transform_actions import TransformingToken
from hacknslassh.utils import distance
import pygame as pg
from hacknslassh.components.image import ImageTransition, ImageTransitionStyle
from hacknslassh.components.in_location import ActiveMarkers, Direction, InLocation
from hacknslassh.components.sight import Sight
from ..gui.utils import combine_RGB_colors
from ..components import Image, DelayCallback, RGB, RedRegeneration, BlueRegeneration, GreenRegeneration, Acting, User, DeathCallback


class UserInputProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for _, (user, acting) in self.world.get_components(User, Acting):
            if user.last_input in acting.actions:
                acting.selected_action = acting.actions[user.last_input]
                user.last_input = ""

class SightTokenProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (sight, token) in self.world.get_components(Sight, IncreasedSightToken):
            if token.on_processor:
                token.on_processor(self.world, ent_id, deltatime)
            for i in range(len(token.values)):
                token.values[i] -= deltatime
                if token.values[i] <= 0:
                    sight.radius -= 1
                    if user := self.world.try_component(ent_id, User):
                        user.mind.process_event("player_status_changed")
                        user.mind.process_event("redraw_ui")

            token.values = [x for x in token.values if x > 0]
            if not token.values:
                self.world.remove_component(ent_id, IncreasedSightToken)

class TransformedTokenProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (token, ) in self.world.get_components(TransformedToken):
            if token.on_processor:
                token.on_processor(self.world, ent_id, deltatime)
            
class ProjectileMovementProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (in_loc, proj, acting, ) in self.world.get_components(InLocation, Projectile, Acting):
            
            if not in_loc.dungeon:
                continue
            
            if target_id := in_loc.dungeon.get_at(in_loc.forward):
                proj.on_hit(self.world, ent_id, target_id)
                in_loc.dungeon.remove_renderable_entity(ent_id)
                in_loc.dungeon = None
                self.world.delete_entity(ent_id)

            elif acting.movement_recoil > 0:
                acting.movement_recoil -= deltatime
                continue
            else:
                x, y, z = in_loc.position
                vx = int(in_loc.direction == Direction.DOWN) - int(in_loc.direction == Direction.UP)
                vy = int(in_loc.direction == Direction.RIGHT) - int(in_loc.direction == Direction.LEFT)
                new_position = (x + vx, y + vy, z)

                if distance(new_position, proj.origin) > proj.range:
                    in_loc.dungeon.remove_renderable_entity(ent_id)
                    in_loc.dungeon = None
                    self.world.delete_entity(ent_id)

                elif in_loc.dungeon.is_in_bound(new_position):
                    in_loc.dungeon.remove_renderable_entity(ent_id)
                    in_loc.position = new_position
                    in_loc.dungeon.set_renderable_entity(ent_id)
                    acting.movement_recoil = Recoil.SHORT / (1 + proj.velocity)

                
                    # self.world.delete_entity(ent_id)

            for other_ent_id, (other_user, other_in_loc, other_sight) in self.world.get_components(User, InLocation, Sight):
                    if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and distance(in_loc.position, other_in_loc.position) <= other_sight.radius:
                        other_user.mind.process_event("redraw_ui")



class DeathProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (rgb, _) in self.world.get_components(RGB, Acting):
            if rgb.red.value <= 0 and not self.world.try_component(ent_id, DeathCallback):
                death_counter = DeathCallback()
                self.world.add_component(ent_id, death_counter)
                self.world.component_for_entity(ent_id, Acting).selected_action = None
                in_location = self.world.component_for_entity(ent_id, InLocation)
                x, y, z = in_location.position
                in_location.dungeon.remove_renderable_entity(ent_id)
                in_location.position = (x, y, 0)
                in_location.active_markers = ActiveMarkers.DEATH
                in_location.dungeon.set_renderable_entity(ent_id)

class DeathCallbackProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (delay_cb, ) in self.world.get_components(DeathCallback):
            delay_cb.delay -= deltatime
            if delay_cb.delay <= 0:
                self.world.remove_component(ent_id, DeathCallback)
                if in_loc := self.world.try_component(ent_id, InLocation):
                    if in_loc.dungeon:
                        in_loc.dungeon.remove_renderable_entity(ent_id)
                        in_loc.dungeon = None
                
                if user := self.world.try_component(ent_id, User):
                    user.mind.process_event("redraw_ui")

                for other_ent_id, (other_acting, ) in self.world.get_components(Acting, ):
                    if other_ent_id != ent_id and other_acting.target == ent_id:
                        other_acting.target = None
                        if (other_user := self.world.try_component(other_ent_id, User)):
                            other_user.mind.process_event("acting_target_updated", other_acting.target)
                
                for other_ent_id, (other_user, other_in_loc, other_sight) in self.world.get_components(User, InLocation, Sight):
                    if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and distance(in_loc.position, other_in_loc.position) <= other_sight.radius:
                        other_user.mind.process_event("redraw_ui")
                    
                self.world.delete_entity(ent_id)
        

class ActionProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (acting,) in self.world.get_components(Acting):
            if acting.selected_action:
                acting.selected_action.use(self.world, ent_id)
                acting.selected_action = None
            if acting.action_recoil > 0:
                acting.action_recoil = max(0, acting.action_recoil - deltatime)
                if user := self.world.try_component(ent_id, User):
                    user.mind.process_event("player_acting_changed")
                    
            if acting.movement_recoil > 0:
                acting.movement_recoil = max(0, acting.movement_recoil - deltatime)
                # if user := self.world.try_component(ent_id, User):
                #     user.mind.process_event("player_acting_changed")

class UpdateTargetProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (acting, sight) in self.world.get_components(Acting, Sight):
            if acting.target:
                target_in_loc = self.world.try_component(acting.target, InLocation)
                if not target_in_loc or not sight.is_visible(target_in_loc.position[0], target_in_loc.position[1]):
                    acting.target = None
                    if user := self.world.try_component(ent_id, User):
                        user.mind.process_event("acting_target_updated", acting.target)
                    return
                
            elif acting.auto_target:
                Target.use(self.world, ent_id)
                
class DelayCallbackProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (delay_cb, ) in self.world.get_components(DelayCallback):
            delay_cb.delay -= deltatime
            if delay_cb.delay <= 0:
                delay_cb.callback(self.world, ent)
                self.world.remove_component(ent, DelayCallback)

class ParryCallbackProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (delay_cb, ) in self.world.get_components(ParryCallback):
            delay_cb.delay -= deltatime
            if delay_cb.delay <= 0:
                delay_cb.callback(self.world, ent)
                self.world.remove_component(ent, ParryCallback)

class TransformingTokenProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (delay_cb, ) in self.world.get_components(TransformingToken):
            delay_cb.delay -= deltatime
            if delay_cb.delay <= 0:
                delay_cb.callback(self.world, ent)
                self.world.remove_component(ent, TransformingToken)
                
class ImageTransitionProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (image_mod,) in self.world.get_components(ImageTransition):
            image_mod.current_delay += deltatime
            if image_mod.current_delay >= image_mod.delay:
                self.world.add_component(ent_id, Image(image_mod.new_surface))
                self.world.remove_component(ent_id, ImageTransition) 
                continue
            
            if image_mod.transition == ImageTransitionStyle.LINEAR:
                d = image_mod.current_delay / image_mod.delay
            elif image_mod.transition == ImageTransitionStyle.QUADRATIC:
                d = (image_mod.current_delay / image_mod.delay)**2
            elif image_mod.transition == ImageTransitionStyle.CUBIC:
                d = (image_mod.current_delay / image_mod.delay)**3
            
            old_surface: pg.Surface = image_mod.old_surface.copy()
            new_surface: pg.Surface = image_mod.new_surface.copy()

            if image_mod.current_delay >= image_mod.delay/2:
                srf = new_surface
                for x in range(srf.get_width()):
                    for y in range(srf.get_height()):
                        r, g, b, a = srf.get_at((x, y))
                        if a > 0:
                            r, g, b = combine_RGB_colors((r, g, b), Color.WHITE, 2*d-1, 2-2*d)
                            srf.set_at((x, y), (r, g, b, a))
                self.world.add_component(ent_id, Image(srf))
            else:
                srf = old_surface
                for x in range(srf.get_width()):
                    for y in range(srf.get_height()):
                        r, g, b, a = srf.get_at((x, y))
                        if a > 0:
                            r, g, b = combine_RGB_colors((r, g, b), Color.WHITE, 1-2*d, 2*d)
                            srf.set_at((x, y), (r, g, b, a))
                self.world.add_component(ent_id, Image(srf))


            if user := self.world.try_component(ent_id, User):
                user.mind.process_event("player_image_changed")
                in_loc = self.world.component_for_entity(ent_id, InLocation)
                for other_ent_id, (other_user, other_in_loc, other_sight) in self.world.get_components(User, InLocation, Sight):
                    if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and distance(in_loc.position, other_in_loc.position) <= other_sight.radius:
                        other_user.mind.process_event("other_player_image_changed", ent_id)
                        other_user.mind.process_event("other_player_info_changed", ent_id)
                        other_user.mind.process_event("redraw_ui")

class RegenerationProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (rgb, red_reg) in self.world.get_components(RGB, RedRegeneration):
            red = rgb.red
            red_reg.frame += 1
            if red_reg.frame >= red_reg.frames_to_regenerate:
                red.value += 1
                if self.world.has_component(ent, User):
                    self.world.component_for_entity(ent, User).mind.emit_event("player_hp_changed")
                red_reg.value -= 1
                red_reg.frame = 0
                if red_reg.value <= 0:
                    self.world.remove_component(ent, RedRegeneration)
        
        for ent, (rgb, blue_reg) in self.world.get_components(RGB, BlueRegeneration):
            blue = rgb.blue
            blue_reg.frame += 1
            if blue_reg.frame >= blue_reg.frames_to_regenerate:
                blue.value += 1
                if self.world.has_component(ent, User):
                    self.world.component_for_entity(ent, User).mind.emit_event("player_mp_changed")
                blue_reg.value -= 1
                blue_reg.frame = 0
                if blue_reg.value <= 0:
                    self.world.remove_component(ent, BlueRegeneration)

        for ent, (rgb, green_reg) in self.world.get_components(RGB, GreenRegeneration):
            green = rgb.green
            green_reg.frame += 1
            if green_reg.frame >= green_reg.frames_to_regenerate:
                green.value += 1
                if self.world.has_component(ent, User):
                    self.world.component_for_entity(ent, User).mind.emit_event("player_rgb_changed")
                green_reg.value -= 1
                green_reg.frame = 0
                if green_reg.value <= 0:
                    self.world.remove_component(ent, GreenRegeneration)

class AiProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (in_loc, sight, ai, acting) in self.world.get_components(InLocation, Sight, Ai, Acting):
            if not in_loc.dungeon:
                continue
            # entities will be sorted by distance because visible tiles is sorted by distance.
            for tx, ty in sight.visible_tiles:
                if _ent_id := in_loc.dungeon.get_at((tx, ty, 1)):
                   if distance(in_loc.position, (tx, ty, 1)) > 3 \
                   and self.world.try_component(_ent_id, User):

                    tx, ty, _ = self.world.component_for_entity(_ent_id, InLocation).position
                    x0, y0, _ = in_loc.position
                    #FIXME: check if there is a wall and in that case don't select the relevant action
                    if tx < x0:
                        acting.selected_action = MoveUp
                    elif tx > x0:
                        acting.selected_action = MoveDown
                    elif ty < y0:
                        acting.selected_action = MoveLeft
                    elif ty > y0:
                        acting.selected_action = MoveRight
                    break
       
            
class SightProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (in_loc, sight, rgb) in self.world.get_components(InLocation, Sight, RGB):
            red = rgb.red
            green = rgb.green
            blue = rgb.blue

            # We rescale to keep luminosity up, although the color changes
            MAX_ALPHA = 255
            rescale = MAX_ALPHA/max(red.value, green.value, blue.value, 1)
            new_sight_color = (int(rescale * red.value), int(rescale * green.value), int(rescale * blue.value))
            updated = False
            if new_sight_color != sight.color:
                sight.color = new_sight_color
                # in_loc.fg = sight.color
                updated = True
            
            if rgb.acumen != sight.radius:
                sight.radius = rgb.acumen
                x, y, _ = in_loc.position
                sight.update_visible_and_visited_tiles((x, y), in_loc.direction, in_loc.dungeon)
                updated = True
            
            if updated:
                if user := self.world.try_component(ent_id, User):
                    user.mind.process_event("player_status_changed")
                    user.mind.process_event("redraw_ui")
                    user.mind.process_event("player_sight_changed")
                
                for other_ent_id, (other_user, other_in_loc, other_sight) in self.world.get_components(User, InLocation, Sight):
                    if other_ent_id != ent_id and other_in_loc.dungeon == in_loc.dungeon and distance(in_loc.position, other_in_loc.position) <= other_sight.radius:
                        other_user.mind.process_event("redraw_ui")
