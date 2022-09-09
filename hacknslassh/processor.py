import esper
from hacknslassh.components.actor import User
from .components.location import InLocation
from .gui.utils import marker_to_urwid_text
from .components import Image, Velocity, Renderable, Position, DelayCallback, Health, HealthRegeneration, Mana, ManaRegeneration, Location


class LocationMovementProcessor(esper.Processor):
    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (pos, vel, loc) in self.world.get_components(Position, Velocity, InLocation):
            if loc.is_free(pos.x, pos.y, pos.z):
                continue


class DelayCallbackProcessor(esper.Processor):
    def process(self):
        for ent, (delay_cb, ) in self.world.get_components(DelayCallback):
            delay_cb.delay -= 1
            if delay_cb.delay <= 0:
                delay_cb.callback(ent)
                self.world.remove_component(ent, DelayCallback)

class RegenerationProcessor(esper.Processor):
    def process(self):
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

class UserLocationRenderProcessor(esper.Processor):
    def process(self):
        for ent, (user, loc) in self.world.get_components(User, Location):
            loc_map = list(base_map)
            for z in range(loc.max_z):
                for y in range(loc.max_y):
                    loc_map.append(" " * x_offset)
                    for x in range(loc.max_x):
                        obj = loc.get_at((x, y, z))
                        t = " "
                        if obj:
                            if obj.has_component(Renderable):
                                renderable: Renderable = obj.get_component(Renderable)
                                if renderable.visibility:
                                    t = marker_to_urwid_text(renderable.marker, renderable.fg, renderable.bg, renderable.visibility)
                        text.append(t)
                    text.append("\n")

                return text

# class RenderProcessor(esper.Processor):
#     def process(self):
#         for ent, (rend) in self.world.get_components(Renderable):
#             # Get the image from the Renderable Component:
#             img = rend.img
#             # Convert the image to a list of strings:
#             text = img_to_urwid_text(img, rend.y, rend.x)
#             # Set the text on the Renderable Component's widget:
#             rend.widget.set_text(text)
