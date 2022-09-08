import esper
import urwid
import pygame as pg
from .components import Image, Velocity, Renderable, Position, DelayCallback


class MovementProcessor(esper.Processor):
    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (pos, vel) in self.world.get_components(Position, Velocity):
            pos


class DelayCallbackProcessor(esper.Processor):
    def process(self):
        for ent, (delay_cb) in self.world.get_components(DelayCallback):
            delay_cb.delay -= 1
            if delay_cb.delay <= 0:
                delay_cb.callback(ent)
                self.world.remove_component(ent, DelayCallback)


# class RenderProcessor(esper.Processor):
#     def process(self):
#         for ent, (rend) in self.world.get_components(Renderable):
#             # Get the image from the Renderable Component:
#             img = rend.img
#             # Convert the image to a list of strings:
#             text = img_to_urwid_text(img, rend.y, rend.x)
#             # Set the text on the Renderable Component's widget:
#             rend.widget.set_text(text)
