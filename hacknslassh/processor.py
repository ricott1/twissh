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

def img_to_urwid_text(
        img: Image, y_offset: int = 0, x_offset: int = 0, x_flip: bool = False, y_flip: bool = False
    ) -> list[tuple[urwid.AttrSpec, str] | str]:
        text = ["\n" * y_offset]
        surface = pg.transform.flip(img.surface, x_flip, y_flip)
        w, h = surface.get_width(), surface.get_height()

        # We loop til h-1 to discard last level of odd-heigth images
        for y in range(0, h - 1, 2):
            text.append(" " * x_offset)
            for x in range(w):
                top_r, top_g, top_b, top_a = surface.get_at((x, y))
                btm_r, btm_g, btm_b, btm_a = surface.get_at((x, y + 1))

                if top_a == 0 and btm_a == 0:
                    t = " "
                # elif top_a > 0 and btm_a == 0:
                #     top_r, top_g, top_b = RGBA_to_RGB(top_r, top_g, top_b, top_a)
                #     top_attr = f"#{top_r:02x}{top_g:02x}{top_b:02x}"
                #     t = (urwid.AttrSpec(top_attr, ""), "▀")
                # elif top_a == 0 and btm_a > 0:
                #     btm_r, btm_g, btm_b = RGBA_to_RGB(btm_r, btm_g, btm_b, btm_a)
                #     btm_attr = f"#{btm_r:02x}{btm_g:02x}{btm_b:02x}"
                #     t = (urwid.AttrSpec(btm_attr, ""), "▄")
                # elif top_a > 0 and btm_a > 0:
                else:
                    top_r, top_g, top_b = RGBA_to_RGB(top_r, top_g, top_b, top_a)
                    top_attr = f"#{top_r:02x}{top_g:02x}{top_b:02x}"
                    btm_r, btm_g, btm_b = RGBA_to_RGB(btm_r, btm_g, btm_b, btm_a)
                    btm_attr = f"#{btm_r:02x}{btm_g:02x}{btm_b:02x}"
                    t = (urwid.AttrSpec(btm_attr, top_attr), "▄")

                text.append(t)

            text.append("\n")

        return text    

def combine_RGB_colors(color1, color2, weight1=1, weight2=1):
    return (int((color1[i] * weight1 + color2[i] * weight2) / (weight1 + weight2)) for i in range(3))


def RGBA_to_RGB(r: int, g: int, b: int, a: int, background: tuple[int] | None = None):
    """
    apply alpha using only RGB channels: https://en.wikipedia.org/wiki/Alpha_compositing
    """
    if background:
        return combine_RGB_colors((r, g, b), background, weight1=a, weight2=255 * (255 - a))
    elif a == 255:
        return (r, g, b)
    return (int(c * a / 255.0) for c in (r, g, b))