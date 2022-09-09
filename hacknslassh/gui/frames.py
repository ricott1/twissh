from hacknslassh.components import Image
from hacknslassh.gui.utils import img_to_urwid_text
import urwid
import time
import pygame as pg

from ..constants import *
from .utils import (
    create_button,
    attr_button,
    SelectableColumns,
)

MIN_HEADER_HEIGHT = 3
MAX_MENU_WIDTH = 48
FOOTER_HEIGHT = 4


class UiFrame(urwid.Frame):
    def __init__(self, body, **kwargs):
        super().__init__(body, **kwargs)
        self.completed = False

    def handle_input(self, _input, pressed_since=0):
        pass

    def on_update(self):
        pass


class WarningFrame(UiFrame):
    def __init__(self, w: int, h: int) -> None:
        super().__init__(
            urwid.ListBox(
                [urwid.Text(f"Please set terminal size to a minimum of {WIDTH}x{HEIGHT} (currently {w}x{h})")]
            )
        )


class SplitHorizontalFrame(UiFrame):
    def __init__(self, widgets, weights=None, update_order=None, focus_column=None):
        self.widgets = widgets
        if not update_order:
            update_order = [i for i in range(len(self.widgets))]
        self.update_order = update_order
        if weights:
            super().__init__(
                urwid.Columns(
                    [("weight", weights[i], self.widgets[i]) for i in range(len(weights))],
                    focus_column=focus_column,
                )
            )
        else:
            super().__init__(urwid.Columns(self.widgets, focus_column=focus_column))
        self._completed = False

    @property
    def completed(self):
        if self._completed:
            return True
        for w in self.widgets:
            if not w.completed:
                return False
        return True

    @completed.setter
    def completed(self, value):
        self._completed = value

    def on_update(self):
        for index in self.update_order:
            if hasattr(self.widgets[index], "on_update"):
                self.widgets[index].on_update()

    def handle_input(self, _input, pressed_since=0):
        for index in self.update_order:
            if hasattr(self.widgets[index], "handle_input"):
                self.widgets[index].handle_input(_input)


class SplitVerticalFrame(UiFrame):
    def __init__(self, widgets, weights=None, given=None, update_order=None, focus_item=None):
        self.widgets = widgets
        if not update_order:
            update_order = [i for i in range(len(self.widgets))]
        self.update_order = update_order
        if weights:
            super().__init__(
                urwid.Pile(
                    [("weight", weights[i], self.widgets[i]) for i in range(len(weights))],
                    focus_item=focus_item,
                )
            )
        elif given:
            super().__init__(
                urwid.Pile(
                    [(given[i], self.widgets[i]) for i in range(len(given))],
                    focus_item=focus_item,
                )
            )
        else:
            super().__init__(urwid.Pile(self.widgets, focus_item=focus_item))
        self._completed = False

    @property
    def completed(self):
        if self._completed:
            return True
        for w in self.widgets:
            if not w.completed:
                return False
        return True

    @completed.setter
    def completed(self, value):
        self._completed = value

    def on_update(self):
        for index in self.update_order:
            if hasattr(self.widgets[index], "on_update"):
                self.widgets[index].on_update()

    def handle_input(self, _input, pressed_since=0):
        for index in self.update_order:
            if hasattr(self.widgets[index], "handle_input"):
                self.widgets[index].handle_input(_input, pressed_since)


class TitleFrame(UiFrame):
    def __init__(self, _title, _attribute=None, _font=urwid.HalfBlock5x4Font()):
        if _attribute:
            _title = [(_attribute, t) for t in _title]
        bigtext = urwid.Pile([urwid.Padding(urwid.BigText(t, _font), "center", None) for t in _title])

        bigtext = urwid.Filler(bigtext)
        super().__init__(bigtext)


class TextSelectionFrame(UiFrame):
    def __init__(self, _options={}):
        self.options = _options
        self.selection = None
        x_offset = 10
        columns = []
        n = len(self.options.keys()) or 1
        box_width = WIDTH // n
        box_height = max([len(s) for key, s in self.options.items()], default=1) + 4
        for key, s in self.options.items():
            btn = create_button(key.center(box_width - 2), on_press=self.select)
            box = urwid.BoxAdapter(
                urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text(s), btn])),
                box_height,
            )
            columns.append((box_width, urwid.AttrMap(box, None, focus_map="line")))

        body = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text("")]))
        header = SelectableColumns(columns)
        # header = urwid.Columns(columns)
        super().__init__(body, header=header, focus_part="header")

    def select(self, *args):
        if len(self.options) == 0:
            return
        index = self.contents["header"][0].focus_col
        selection = [opt for key, opt in self.options.items()][index]
        self.selection = selection


class OverlayFrame(UiFrame):
    def __init__(self, top, bottom, *args, top_linebox=True, **kwargs):
        self.top = top
        self.bottom = bottom
        if top_linebox:
            self.full_body = urwid.Overlay(urwid.LineBox(self.top), self.bottom, *args, **kwargs)
        else:
            self.full_body = urwid.Overlay(self.top, self.bottom, *args, **kwargs)

        super().__init__(self.full_body)
        self.top_is_visible = True

    def on_update(self):
        self.top.on_update()
        self.bottom.on_update()

    def handle_input(self, _input):
        self.top.handle_input(_input)
        self.bottom.handle_input(_input)

    def toggle_top_view(self):
        if self.top_is_visible:
            self.contents["body"] = (self.bottom, None)
            self.top_is_visible = False
        else:
            self.contents["body"] = (self.full_body, None)
            self.top_is_visible = True


class VerticalSelectionFrame(UiFrame):
    def __init__(self, _options):
        self.options = _options
        max_width = max([len(opt) for opt in self.options], default=1)
        self.buttons = []
        for opt in self.options:
            btn = create_button(
                opt.center(max_width),
                on_press=lambda btn, selection=opt: self.confirm_selection(selection),
            )
            self.buttons.append(btn)
        btns = [
            urwid.LineBox(
                btn,
                tlcorner=" ",
                tline=" ",
                lline=" ",
                trcorner=" ",
                blcorner=" ",
                rline=" ",
                bline=" ",
                brcorner=" ",
            )
            for btn in self.buttons
        ]
        self.walker = urwid.SimpleFocusListWalker(btns)
        super().__init__(urwid.ListBox(self.walker))
        self.completed = False
        self.selection = None
        self.index = 0
        self.draw_selection_box(self.index)

    def confirm_selection(self, selection):
        self.selection = selection
        self.completed = True

    def on_update(self):
        index = self.contents["body"][0].focus_position
        if index != self.index:
            self.index = index
            self.draw_selection_box(self.index)

    def draw_selection_box(self, index):
        btns = [
            urwid.LineBox(btn)
            if i == index
            else urwid.LineBox(
                btn,
                tlcorner=" ",
                tline=" ",
                lline=" ",
                trcorner=" ",
                blcorner=" ",
                rline=" ",
                bline=" ",
                brcorner=" ",
            )
            for i, btn in enumerate(self.buttons)
        ]
        self.walker = urwid.SimpleFocusListWalker(btns)
        self.walker.set_focus(index)
        self.contents["body"] = (urwid.ListBox(self.walker), None)


class VerticalFocusSelectionFrame(UiFrame):
    def __init__(self, _options):
        self.options = _options
        max_width = max([len(opt) for opt in self.options], default=1)
        self.buttons = []
        for opt in self.options:
            btn = create_button(
                opt.center(max_width),
                on_press=lambda btn, selection=opt: self.confirm_selection(selection),
            )
            btn = urwid.AttrMap(btn, None, focus_map="line")
            self.buttons.append(btn)
        self.walker = urwid.SimpleFocusListWalker(self.buttons)
        super().__init__(urwid.ListBox(self.walker))
        self.completed = False
        self.selection = None
        self.index = 0

    def confirm_selection(self, selection):
        self.selection = selection
        self.completed = True


class TextFrame(UiFrame):
    def __init__(self, text=[""]):
        self.walker = urwid.SimpleFocusListWalker([urwid.Text(t) for t in text])
        listbox = urwid.ListBox(self.walker)
        super().__init__(listbox)

    def update(self, text):
        self.walker[:] = [urwid.Text(t) for t in text]


class SpeechFrame(UiFrame):
    VERTICAL_OFFSET = 5
    NEXT = f"\n\n[Press {NEXT_KEY} to continue]"

    def __init__(self, _speeches=[]):
        self.speeches = ["\n" * self.VERTICAL_OFFSET + s + self.NEXT for s in _speeches]
        self.walker = urwid.SimpleFocusListWalker([urwid.Text("")])
        self.start = time.time()
        self.speech_idx = 0
        self.quick_text = False
        self.speech_over = False
        listbox = urwid.ListBox(self.walker)
        super().__init__(listbox)

    def on_update(self):
        self.update_speech()

    def handle_input(self, _input, pressed_since=0):
        if _input == NEXT_KEY:
            if not self.quick_text:
                self.quick_text = True
            if self.speech_over:
                self.next_speech()

    def update_speech(self):
        _speech = self.speeches[self.speech_idx]
        if self.quick_text:
            _idx = len(_speech)
        else:
            _idx = int((time.time() - self.start) / FRAME_RATE)

        _text = _speech[:_idx]
        if _idx == len(_speech):
            self.speech_over = True
        if _text:
            self.walker.contents[:] = [urwid.Text(_text)]

    def next_speech(self):
        self.speech_idx += 1
        if self.speech_idx >= len(self.speeches):
            self.speech_idx = -1
        else:
            self.start = time.time()
            self.speech_over = False
            self.quick_text = False


class MovingTextFrame(UiFrame):
    def __init__(
        self,
        _text=[],
        _height=20,
        _speed=1,
        _vertical_offset=20,
        align="center",
        stop_at=0,
    ):
        if align == "center":
            self.text = ["\n"] * _vertical_offset + [t.center(WIDTH) + "\n" for t in _text]
        else:
            self.text = ["\n"] * _vertical_offset + [t + "\n" for t in _text]
        self.height = _height
        self.speed = _speed
        self.walker = urwid.SimpleListWalker([urwid.Text("")])
        self.line_offset = 0
        self.quick_text = False
        self.completed = False
        self.stop_at = stop_at
        listbox = urwid.ListBox(self.walker)
        super().__init__(listbox)

    def on_update(self, deltatime):
        if self.completed:
            return
        self.line_offset += deltatime * self.speed * (1 + int(self.quick_text))
        if self.line_offset >= len(self.text) - self.stop_at:
            # self.walker.contents[:] = [urwid.Text("")]
            self.completed = True
        else:
            _end = int(min(self.line_offset + self.height, len(self.text)))
            lines = self.text[int(self.line_offset) : _end]
            self.walker.contents[:] = [urwid.Text(lines)]

    def handle_input(self, _input, pressed_since=0):
        if _input == NEXT_KEY:
            self.quick_text = not self.quick_text


class EntryFrame(UiFrame):
    VERTICAL_OFFSET = 5

    def __init__(self, text, size=(20, 1), caption="", on_finish=None):
        self.entry = urwid.Edit(caption=caption)
        self.size = size
        self.selection = None
        super().__init__(
            urwid.ListBox([urwid.Text("\n" * self.VERTICAL_OFFSET + text)]),
            footer=self.entry,
            focus_part="footer",
        )

    def handle_input(self, _input, pressed_since=0):
        if _input == "enter":
            _name = self.entry.get_edit_text().strip()
            if len(_name) > 0:
                self.selection = _name
        else:
            self.keypress(self.size, _input)


class ImageFrame(UiFrame):
    def __init__(
        self, image: Image, background_attr=None, x_offset: int = 0, x_flip: bool = False, y_flip: bool = False
    ):
        self.background_attr = background_attr
        text = img_to_urwid_text(image, x_offset=x_offset, x_flip=x_flip, y_flip=y_flip)

        _walker = urwid.SimpleListWalker(
            [
                urwid.Text(
                    text,
                    wrap="clip",
                )
            ]
        )
        self.listbox = urwid.ListBox(_walker)
        super().__init__(self.listbox)
