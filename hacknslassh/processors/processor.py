import esper
from hacknslassh.components.tokens import IncreasedSightToken
import pygame as pg
from hacknslassh.components.image import ImageTransition, ImageTransitionStyle
from hacknslassh.components.in_location import InLocation
from ..gui.utils import combine_RGB_colors
from ..components import Image, DelayCallback, Health, HealthRegeneration, Mana, ManaRegeneration, Acting, User, DeathCallback


class UserInputProcessor(esper.Processor):
    def process(self, dt: float) -> None:
        for ent_id, (user, acting) in self.world.get_components(User, Acting):
            if user.last_input in acting.actions:
                acting.selected_action = acting.actions[user.last_input]
                user.last_input = ""

class SightTokenProcessor(esper.Processor):
    def process(self, dt: float) -> None:
        for ent_id, (in_loc, sight_token) in self.world.get_components(InLocation, IncreasedSightToken):
            user: User = self.world.try_component(ent_id, User)
            reduction_signalled = False
            for i in range(len(sight_token.values)):
                sight_token.values[i] -= dt
                if sight_token.values[i] <= 0:
                    in_loc.sight_radius -= 1
                    if user and not reduction_signalled:
                        user.mind.process_event("redraw_local_ui")
                        user.mind.process_event("player_status_changed")
                        reduction_signalled = True

            sight_token.values = [x for x in sight_token.values if x > 0]
            if not sight_token.values:
                self.world.remove_component(ent_id, IncreasedSightToken)
            

class DeathProcessor(esper.Processor):
    def process(self, dt: float) -> None:
        for ent_id, (health, _) in self.world.get_components(Health, Acting):
            if health.value <= 0 and not self.world.try_component(ent_id, DeathCallback):
                death_counter = DeathCallback(lambda: self.world.delete_entity(ent_id))
                self.world.add_component(ent_id, death_counter)
                self.world.component_for_entity(ent_id, Acting).selected_action = None
                in_location = self.world.component_for_entity(ent_id, InLocation)
                x, y, z = in_location.position
                in_location.dungeon.remove_renderable_entity(ent_id)
                in_location.position = (x, y, 0)
                in_location.marker = "X"
                in_location.dungeon.set_renderable_entity(ent_id)

class ActionProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent_id, (acting,) in self.world.get_components(Acting):
            if acting.selected_action:
                acting.selected_action.use(self.world, ent_id)
                acting.selected_action = None
            if acting.action_recoil > 0:
                acting.action_recoil = max(0, acting.action_recoil - deltatime)
            if acting.movement_recoil > 0:
                acting.movement_recoil = max(0, acting.movement_recoil - deltatime)

class DelayCallbackProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (delay_cb, ) in self.world.get_components(DelayCallback):
            delay_cb.delay -= deltatime
            if delay_cb.delay <= 0:
                delay_cb.callback(ent)
                self.world.remove_component(ent, DelayCallback)
                
class ImageTransitionProcessor(esper.Processor):
    def process(self, deltatime: float) -> None:
        for ent, (image, image_mod,) in self.world.get_components(Image, ImageTransition):
            image_mod.current_delay += deltatime
            if image_mod.current_delay >= image_mod.delay:
                self.world.add_component(ent, Image(image_mod.new_surface))
                self.world.remove_component(ent, ImageTransition) 
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
                            r, g, b = combine_RGB_colors((r, g, b), (255, 255, 255), 2*d-1, 2-2*d)
                            srf.set_at((x, y), (r, g, b, a))
                self.world.add_component(ent, Image(srf))
            else:
                srf = old_surface
                for x in range(srf.get_width()):
                    for y in range(srf.get_height()):
                        r, g, b, a = srf.get_at((x, y))
                        if a > 0:
                            r, g, b = combine_RGB_colors((r, g, b), (255, 255, 255), 1-2*d, 2*d)
                            srf.set_at((x, y), (r, g, b, a))
                self.world.add_component(ent, Image(srf))


            if user := self.world.try_component(ent, User):
                user.mind.process_event("player_image_changed")

class RegenerationProcessor(esper.Processor):
    def process(self, deltatime: float):
        for ent, (health, health_reg) in self.world.get_components(Health, HealthRegeneration):
            health_reg.frame += 1
            if health_reg.frame >= health_reg.frames_to_regenerate:
                health.value += 1
                if self.world.has_component(ent, User):
                    self.world.component_for_entity(ent, User).mind.emit_event("player_hp_changed")
                health_reg.value -= 1
                health_reg.frame = 0
                if health.value >= health.max_value or health_reg.value <= 0:
                    health.value = health.max_value
                    self.world.remove_component(ent, HealthRegeneration)
        
        for ent, (mana, mana_reg) in self.world.get_components(Mana, ManaRegeneration):
            mana_reg.frame += 1
            if mana_reg.frame >= mana_reg.frames_to_regenerate:
                mana.value += 1
                if self.world.has_component(ent, User):
                    self.world.component_for_entity(ent, User).mind.emit_event("player_mp_changed")
                mana_reg.value -= 1
                mana_reg.frame = 0
                if mana.value >= mana.max_value or mana_reg.value <= 0:
                    mana.value = mana.max_value
                    self.world.remove_component(ent, ManaRegeneration)


# class DungeonRendererProcessor(esper.Processor):
#     def process(self, deltatime: float):
#         for ent, (in_loc) in self.world.get_components(InLocation):
            