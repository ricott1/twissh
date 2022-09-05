from __future__ import annotations

import urwid
import pygame as pg
from ..constants import WIDTH, HEIGHT

PALETTE = [
    # (None, "yellow", "light red"),
    ("line", "black", "white", "standout"),
    ("top", "white", "black"),
    ("black", "black", "black"),
    ("background", "white", "black"),
    ("background_focus", "black", "white", "standout"),
    ("name", "yellow", "black"),
    ("green", "light green", "black"),
    ("yellow", "yellow", "black"),
    ("red", "light red", "black"),
]


class SelectableColumns(urwid.Columns):
    def __init__(self, widget_list, focus_column=None, dividechars=0, on_keypress=None):
        super().__init__(widget_list, dividechars, focus_column)
        self.on_keypress = on_keypress

    def keypress(self, size, key):
        super().keypress(size, key)
        if self.on_keypress and key != "enter":
            self.on_keypress()

    def focus_next(self):
        try:
            self.focus_position += 1
        except ValueError:
            pass

    def focus_previous(self):
        try:
            self.focus_position -= 1
        except ValueError:
            pass


class ButtonLabel(urwid.SelectableIcon):
    def set_text(self, label):
        """
        set_text is invoked by Button.set_label
        """
        self.__super.set_text(label)
        self._cursor_position = len(label) + 1


class MyButton(urwid.Button):
    """
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged
    """

    button_left = "["
    button_right = "]"

    def __init__(self, label, on_press=None, user_args=None, borders=True, disabled=False):
        self._label = ButtonLabel("")
        if borders:
            cols = urwid.Columns(
                [
                    ("fixed", len(self.button_left), urwid.Text(self.button_left)),
                    self._label,
                    ("fixed", len(self.button_right), urwid.Text(self.button_right)),
                ],
                dividechars=1,
            )
        else:
            cols = urwid.Columns([self._label], dividechars=0)

        super(urwid.Button, self).__init__(cols)

        self.disabled = disabled
        if on_press:
            urwid.connect_signal(self, "click", on_press, user_args=user_args)

        self.set_label(label)
        self.lllavel = label

    def selectable(self):
        return not self.disabled


def terminal_size(scr=urwid.raw_display.Screen()):
    return scr.get_cols_rows()


def attr_button(label, attr_map=None, focus_map="line", **kwargs):
    btn = create_button(label, **kwargs)
    return urwid.AttrMap(btn, attr_map, focus_map=focus_map)


def create_button(label, align="center", **kwargs):
    btn = MyButton(label, **kwargs)
    btn._label.align = align
    return btn


def combine_RGB_colors(color1, color2, weight1=1, weight2=1):
    return (int((color1[i] * weight1 + color2[i] * weight2) / (weight1 + weight2)) for i in range(3))


def RGBA_to_RGB(r, g, b, a, background=None):
    """
    apply alpha using only RGB channels: https://en.wikipedia.org/wiki/Alpha_compositing
    """
    if background:
        return combine_RGB_colors((r, g, b), background, weight1=a, weight2=255 * (255 - a))
    elif a == 255:
        return (r, g, b)
    return (int(c * a / 255.0) for c in (r, g, b))


def interpolate_colors(color1, color2, value):
    return [int(round(x + (y - x) * value)) for x, y in zip(color1, color2)]


def light_up(r, g, b, a, add_a=255):
    if a > 0:
        return (r, g, b, min(255, a + add_a))
    return (r, g, b, a)


def illumination_pixel_effect(expression, rgba_override, max_effect_distance=10):
    def color_modifier(x, y, r, g, b, a):
        distance = (expression(x, y) ** 2) ** 0.5
        if distance <= max_effect_distance:
            return interpolate_colors(
                (r, g, b, a),
                rgba_override(r, g, b, a),
                1 - distance / max_effect_distance,
            )
        return [r, g, b, a]

    return lambda x, y, r, g, b, a: color_modifier(x, y, r, g, b, a)


def crop_image(image, w=WIDTH, h=HEIGHT, x=0, y=0, off_x=0, off_y=0):
    cropped = pg.Surface((w, h))
    cropped.blit(image, (x, y), (off_x, off_y, w, h))
    return cropped

    # def pil_img_to_text(img, x_offset=0, y_offset=0, custom={}, extra={}):
    """
    {100 fixed
    95: skin 
    90: skin shadow
    85: hair 
    80: hair shadow
    75: eyes
    70: trousers
    65: trousers shadow
    }
    """
    # masks = {
    #     242: "skin",
    #     230: "skin-shadow",
    #     217: "hair" ,
    #     204: "hair-shadow",
    #     191: "eyes",
    #     179: "trousers",
    #     166: "trousers-shadow"
    #     }

    # pixels = list(img.getdata())
    # width, height = img.size
    # text = ["\n" *y_offset]
    # for i in range(height):
    #     text.append(("background", "  "*x_offset))
    #     for j in range(i * width, (i + 1) * width):
    #         r, g, b, a = pixels[j]
    #         v = rgbToHex(r, g, b)
    #         if a in masks and masks[a] in custom:
    #             c = custom[masks[a]]
    #             text.append((urwid.AttrSpec(c, c, colors=256), "  "))
    #         elif a == 0:
    #             text.append(("background", "  "))
    #         else:
    #             text.append((urwid.AttrSpec(v, v, colors=256), "  "))
    #     text.append("\n")
    # return text
