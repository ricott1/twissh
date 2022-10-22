from __future__ import annotations

import urwid
import pygame as pg

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

EMPTY_FILL = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))

class SelectableListBox(urwid.ListBox):
    def __init__(self, body):
        super(SelectableListBox, self).__init__(body)

    def focus_next(self):
        try:
            self.focus_position += 1
        except IndexError:
            pass

    def focus_previous(self):
        try:
            self.focus_position -= 1
        except IndexError:
            pass


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


def marker_to_urwid_text(marker: str, fg: tuple[int, int, int], bg: tuple[int, int, int] | None, a: int = 255) -> tuple[urwid.AttrSpec, str]: 
    f_r, f_g, f_b = RGBA_to_RGB(*fg, a)
    f_attr = f"#{f_r:02x}{f_g:02x}{f_b:02x}"
    if bg:
        b_r, b_g, b_b = RGBA_to_RGB(*bg, a)
        b_attr = f"#{b_r:02x}{b_g:02x}{b_b:02x}"
    else:
        b_attr = ""
    return (urwid.AttrSpec(f_attr, b_attr), marker)

def img_to_urwid_text(
    img, x_offset: int = 0, y_offset: int = 0, x_flip: bool = False, y_flip: bool = False
) -> list[tuple[urwid.AttrSpec, str] | str]:
    text = ["\n" * y_offset]
    surface = pg.transform.flip(img, x_flip, y_flip)
    w, h = surface.get_width(), surface.get_height()

    # We loop til h-1 to discard last level of odd-heigth images
    for y in range(0, h - 1, 2):
        text.append(" " * x_offset)
        for x in range(w):
            top_r, top_g, top_b, top_a = surface.get_at((x, y))
            btm_r, btm_g, btm_b, btm_a = surface.get_at((x, y + 1))

            if top_a == 0 and btm_a == 0:
                t = " "
            elif top_a > 0 and btm_a == 0:
                top_r, top_g, top_b = RGBA_to_RGB(top_r, top_g, top_b, top_a)
                top_attr = f"#{top_r:02x}{top_g:02x}{top_b:02x}"
                t = (urwid.AttrSpec(top_attr, ""), "▀")
            elif top_a == 0 and btm_a > 0:
                btm_r, btm_g, btm_b = RGBA_to_RGB(btm_r, btm_g, btm_b, btm_a)
                btm_attr = f"#{btm_r:02x}{btm_g:02x}{btm_b:02x}"
                t = (urwid.AttrSpec(btm_attr, ""), "▄")
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


def combine_RGB_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], weight1: float=1, weight2:float=1) -> tuple[int, int, int]:
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