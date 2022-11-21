# encoding: utf-8

from __future__ import annotations
from enum import Enum
import time
from typing import TYPE_CHECKING
from mathclassh.math_skills import FieldNames

from twissh.server import UrwidMind

if TYPE_CHECKING:
    from mathclassh.master import MathClassH
from ..mathematician import GENDER, Mathematician
from .frames import DoubleLineBox, NoLineBox, SolidLineBox
from .utils import img_to_urwid_text
from typing import Callable
import urwid

from urwid import raw_display

SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()

MENU_WIDTH = 30
FOOTER_HEIGHT = 4
IMAGE_MAX_HEIGHT = 20


class Scene(object):
    def __init__(self, mind: UrwidMind, *args, palette=None, **kwargs):
        # mixin class for frame and scene properties
        self.palette = palette
        super().__init__(*args, **kwargs)
        self.mind = mind
        self.master: MathClassH = self.mind.master
    
    def handle_input(self, _input: str) -> None:
        pass

    def restart(self) -> None:
        pass

    def register_callback(self, event_name: str, callback: Callable, priority: int = 0) -> None:
        self.mind.register_callback(event_name, callback, priority)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        self.mind.process_event(event_name, *args, **kwargs)
        
class TitleFrame(urwid.Frame):
    def __init__(self, _title, _attribute=None, _font=urwid.HalfBlock5x4Font()):
        if _attribute:
            _title = [(_attribute, t) for t in _title]
        bigtext = urwid.Pile([urwid.Padding(urwid.BigText(t, _font), "center", None) for t in _title])
        super().__init__(urwid.Filler(bigtext))


class SideView(Scene, urwid.Columns):
    def __init__(self, mind, left, right) -> None:
        self.left = left
        self.right = right
        super().__init__(mind, [urwid.WidgetDisable(urwid.LineBox(self.left)), urwid.WidgetDisable(NoLineBox(self.right))], focus_column = 0)
    
    def handle_input(self, _input: str) -> None:
        if _input == "left" and self.focus_position != 0:
            self.focus_position = 0
            self.contents[0] = (urwid.WidgetDisable(urwid.LineBox(self.left)), ('weight', 1, False))
            self.contents[1] = (urwid.WidgetDisable(NoLineBox(self.right)), ('weight', 1, False))
        elif _input == "right" and self.focus_position != 1:
            self.focus_position = 1
            self.contents[0] = (urwid.WidgetDisable(NoLineBox(self.left)), ('weight', 1, False))
            self.contents[1] = (urwid.WidgetDisable(urwid.LineBox(self.right)), ('weight', 1, False))
        elif self.focus_position == 0:
            self.left.handle_input(_input)
        elif self.focus_position == 1:
            self.right.handle_input(_input)

class DisplayView(str, Enum):
    DESCRIPTION = 'description'
    STATS = 'stats'

class DisplayMathematician(Scene, urwid.Frame):
    def __init__(self, mind, mathematician: Mathematician) -> None:
        # self.title = urwid.WidgetDisable(TitleFrame(["Math Class H"]))
        self.mathematician = mathematician
        self.master = mind.master
        # img = ImageCollection.BLUE_FRAME.copy()
        # img.blit(self.mathematician.portrait, (2, 3))
        img_walker = urwid.SimpleListWalker([urwid.Text(img_to_urwid_text(self.mathematician.portrait))])
        portrait = NoLineBox(SolidLineBox(urwid.ListBox(img_walker)))

        self.side_text = urwid.Text("\n" + self.general_info())
        side = urwid.ListBox(urwid.SimpleListWalker([self.side_text]))
        top = urwid.Columns([(self.mathematician.portrait.get_width() + 4, portrait), side])
        self.middle_text = urwid.Text(self.description())
        description = urwid.ListBox(urwid.SimpleListWalker([self.middle_text]))
        self.bottom_text = urwid.Text(" Press 's' to see stats")
        footer = urwid.ListBox(urwid.SimpleListWalker([self.bottom_text]))
        self.body = urwid.Pile([(self.mathematician.portrait.get_height()//2 + 4, top), description, (1, footer)])
        super().__init__(mind, self.body)
        self.view = DisplayView.DESCRIPTION
    
    def handle_input(self, _input: str) -> None:
        if _input == "s":
            if self.view != DisplayView.STATS:
                self.middle_text.set_text(self.stats_description())
                self.bottom_text.set_text(" Press 'd' to see description")
                self.view = DisplayView.STATS
        elif _input == "d":   
            if self.view != DisplayView.DESCRIPTION:
                self.middle_text.set_text(self.description())
                self.bottom_text.set_text(" Press 's' to see stats")
                self.view = DisplayView.DESCRIPTION

    def description(self) -> str:
        match self.mathematician.gender:
            case GENDER.MALE:
                pronoun = "He is"
            case GENDER.FEMALE:
                pronoun = "She is"
            case _:
                pronoun = "They are"

        research_group = self.master.research_groups[self.mathematician.research_group]
        uni = self.master.universities[research_group.university]
        city = self.master.cities[uni.city]
        contract = self.mathematician.contract
        if contract:
            work = f"{pronoun} currently {contract.role} at {uni.name} in {city.name}, {city.country}. The contract will end on {time.strftime('%d-%m-%Y', time.localtime(contract.end_date))}.\n"
        else:
            work = f"{pronoun} currently unemployed.\n"
        # contract = f"{pronoun} is currently under contract until {time.strftime('%Y-%m-%d', time.localtime(self.contract.end_date))}, earning {self.contract.salary} per year.\n"

        match self.mathematician.happiness:
            case x if x < 20:
                happiness = f"{pronoun} miserable "
            case x if x < 40:
                happiness = f"{pronoun} unhappy "
            case x if x < 60:
                happiness = f"{pronoun} alright "
            case x if x < 80:
                happiness = f"{pronoun} happy "
            case x if x <= 100:
                happiness = f"{pronoun} ecstatic "
            case _:
                happiness = f"{pronoun} in a state of confusion "
        
        match self.mathematician.fame:
            case x if x < 20:
                fame = f"and unknown.\n"
            case x if x < 40:
                fame = f"and a local celebrity.\n"
            case x if x < 70:
                fame = f"and a national celebrity.\n"
            case x if x < 90:
                fame = f"and a global celebrity.\n"
            case _:
                fame = f"and will be remembered forever.\n"

        return "\n" + work + happiness + fame

    def general_info(self) -> str:
        city = self.master.cities[self.mathematician.born_in]
        return f"{self.mathematician.name} {self.mathematician.last_name} is a {self.mathematician.age}-year-old from {city.name}, {city.country}."
    
    def colored_skill_text(self, value: int) -> tuple[str, str]:
        match value:
            case x if x < 4:
                return (urwid.AttrSpec("light red", ""), "very low")
            case x if x < 8:
                return (urwid.AttrSpec("yellow", ""), "low")
            case x if x < 13:
                return (urwid.AttrSpec("white", ""), "average")
            case x if x < 17:
                return (urwid.AttrSpec("dark green", ""), "high")
            case x if x <= 20:
                return (urwid.AttrSpec("light blue", ""), "very high")
            case _:
                return (urwid.AttrSpec("white", ""), "unknown")

    def stats_description(self) -> str:
        stats = self.mathematician.stats
        col = self.colored_skill_text
        text = []
        for name, stat in stats.items():
            if stat:
                tot = sum([value for _, value in stat.items()])//len(stat)
                text += [f"\n{name}: ", col(tot)]
        #     for subname, value in stat.items():
        #         text += [f"\n  {subname}: ", col(value)]
        return text