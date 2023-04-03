# encoding: utf-8

import random
from typing import Callable, Type

import esper
from typing import TYPE_CHECKING
from hacknslassh.components.acting import Acting
from hacknslassh.components.tokens import ColorDescriptor
from hacknslassh.dungeon import render_dungeon_map, render_dungeon_minimap
if TYPE_CHECKING:
    from hacknslassh.master import HackNSlassh

import urwid

from hacknslassh.components.characteristics import RGB
from hacknslassh.components.in_location import InLocation
from hacknslassh.components.description import Info, Language
from hacknslassh.components.user import User
from hacknslassh.components.sight import Sight
from hacknslassh.constants import *
from twissh.server import UrwidMind

from ..components import (Component, GenderType, RedRegeneration, GreenRegeneration, Image,
                          ImageCollection, BlueRegeneration, QuickItemSlots)
from ..gui import frames
from .utils import EMPTY_FILL, RGBA_to_RGB, attr_button

MENU_WIDTH = 30
FOOTER_HEIGHT = 4
IMAGE_MAX_HEIGHT = 19


class Scene(object):
    def __init__(self, mind: UrwidMind, *args, palette=None, **kwargs):
        # mixin class for frame and scene properties
        self.palette = palette
        
        self.mind = mind
        self.master: HackNSlassh = self.mind.master
        super().__init__(*args, **kwargs)

    @property
    def player_id(self) -> int:
        if self.mind.avatar.uuid.bytes in self.master.player_ids:
            return self.master.player_ids[self.mind.avatar.uuid.bytes]
        else:
            return 0
    
    @property
    def screen_size(self) -> tuple[int, int]:
        return self.mind.screen_size
    
    @property
    def world(self) -> esper.World:
        return self.mind.master.world

    def get_player_component(self, component: Type[Component]) -> Component | None:
        return self.world.try_component(self.player_id, component)

    def input_handler(self, _input: str) -> bool:
        return False

    def restart(self) -> None:
        pass

    def register_callback(self, event_name: str, callback: Callable, priority: int = 0) -> None:
        self.mind.register_callback(event_name, callback, priority)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        self.mind.process_event(event_name, *args, **kwargs)
        

class CharacterSelectionFrame(Scene, urwid.Pile):
    options = {
        "Human": {
            "description": "Beware their nerdy glasses and their nerdy ways.",
            "bonus": "Strength +1, Hit points +4",
            "abilities": "Charge and parry",
        },
        # "Bard": {
        #     "description": "Tell them a story and they'll sing you a song.",
        #     "bonus": "Strength +1, Constitution +1, Hit points +6",
        #     "abilities": "Demolish and parry",
        # },
        "Orc": {
            "description": "One orc to rule them all.",
            "bonus": "Intelligence +1",
            "abilities": "Fireball, teleport and ice wall",
        },
        "Elf": {
            "description": "If I had a bow, I would shoot you.",
            "bonus": "Dexterity +1, Intelligence +1, Hit points +1",
            "abilities": "Sneak attack, hide and trap",
        },
        "Dwarf": {
            "description": "The grey beards are coming.",
            "bonus": "Charisma +1, Dexterity +1, Intelligence +1, Hit points +2",
            "abilities": "Sing and summon",
        },
        # "Devil": {
        #     "description": "You'll be the devil's next meal.",
        #     "bonus": "Strength +1, Constitution +1, Hit points +6",
        #     "abilities": "Fireball, teleport and ice wall",
        # }
    }

    def __init__(self, mind) -> None:
        self.options_keys = list(self.options.keys())
        self.title = urwid.WidgetDisable(frames.TitleFrame(["Hack'n'SlaSSH"]))
        max_width = max([len(opt) for opt in self.options], default=1)
        self.buttons = [
            attr_button(
                f"<- {opt.center(max_width)} ->",
                on_press = self.select_character,
            )
            for opt in self.options
        ]

        self.row_index = 0
        self.column_index = 1
        selection = self.options_keys[self.row_index]

        left_img = CHARACTERS_SELECTION_FRAMES[GenderType.FEMALE]["unselected"][selection]
        right_img = CHARACTERS_SELECTION_FRAMES[GenderType.MALE]["unselected"][selection]
        self.description_text = urwid.Text(self.options[selection]["description"])
        self.menu_walker = urwid.SimpleFocusListWalker(self.buttons + [urwid.WidgetDisable(self.description_text)])
        self.menu = urwid.ListBox(self.menu_walker)
        self.main = urwid.Columns(
            [(20, left_img), self.menu, (20, right_img)], focus_column=self.column_index, min_width=20
        )
        
        super().__init__(mind, [(4, self.title), self.main], focus_item=1)
        
    def handle_input(self, _input, pressed_since=0):
        if _input == "enter":
            self.select_character()
        elif _input in ("up", "down", "left", "right"):
            self.update()
        
    def select_character(self, btn=None):
        row_index = self.menu.focus_position
        column_index = self.main.focus_position
        selection = self.options_keys[row_index]
        if column_index == 0:
            gender = GenderType.FEMALE
        elif column_index == 2:
            gender = GenderType.MALE
        else:
            gender = random.choice([GenderType.FEMALE, GenderType.MALE])
        player_id = self.master.register_new_player(self.mind, selection, gender)
        self.emit_event("new_player")
    
    def keypress(self, size, key):
        key = super().keypress(size, key)
        self.update()
        self.emit_event("redraw_local_ui")
        return key

    def update(self) -> None:
        row_index = self.menu.focus_position
        column_index = self.main.focus_position

        if self.row_index != row_index or self.column_index != column_index:
            selection = self.options_keys[row_index]
            self.description_text.set_text(self.options[selection]["description"])
            left_img = (
                CHARACTERS_SELECTION_FRAMES[GenderType.FEMALE]["selected"][selection]
                if column_index == 0
                else CHARACTERS_SELECTION_FRAMES[GenderType.FEMALE]["unselected"][selection]
            )
            right_img = (
                CHARACTERS_SELECTION_FRAMES[GenderType.MALE]["selected"][selection]
                if column_index == 2
                else CHARACTERS_SELECTION_FRAMES[GenderType.MALE]["unselected"][selection]
            )

            self.main.contents[0] = (left_img, ("given", 20, False))
            self.main.contents[2] = (right_img, ("given", 20, False))
            self.row_index = row_index
            self.column_index = column_index


class NetHackFrame(Scene, urwid.Frame):
    def __init__(self, mind) -> None:
        self.map = MapFrame(mind)
        self.menu = MenuFrame(mind)
        self.bottom_menu = BottlesAndQuickItemFrame(mind)
        # self.log = LogFrame(mind, visible_lines=FOOTER_HEIGHT-2)

        self.left = urwid.Pile([self.map, (FOOTER_HEIGHT, self.bottom_menu)])
        self.right = self.menu

        self.bottom = urwid.Columns([self.bottom_menu, (MENU_WIDTH, urwid.Columns(self.bottom_menu.quick_items_columns))])
        self.full_view_body = urwid.Columns([self.left, (MENU_WIDTH, self.menu)])
        self.partial_view_body = urwid.Pile([self.map, (FOOTER_HEIGHT, self.bottom)])
        super().__init__(mind, urwid.WidgetDisable(self.full_view_body))
        self.full_menu_view = True
        self.center_map_camera()
        self.register_callback("center_map_camera", self.center_map_camera)
        self.input_handlers = []
        self.add_input_handler(0, self.bottom_menu.input_handler)
        self.add_input_handler(2, self.input_handler)
        self.add_input_handler(1, self.menu_input_handler)
    
    def add_input_handler(self, priority: int, callback: Callable) -> None:
        self.input_handlers.append({"priority": priority, "callback": callback})
        self.input_handlers.sort(key=lambda x: x["priority"])

    def menu_input_handler(self, _input: str) -> bool:
        if self.menu.input_handler_full_view(_input) and not self.full_menu_view:
            self.toggle_menu_view()
            return True
        return False
    
    def input_handler(self, _input: str) -> bool:
        if _input == KeyMap.TOGGLE_FULL_MENU:
            self.toggle_menu_view()
            if not self.full_menu_view:
                if self.bottom_menu.menu_view == self.bottom_menu.quick_items_columns:
                    self.bottom_menu.toggle_view()
            return True
        
        if _input == KeyMap.EXIT_CHAT_MENU:
            self.full_menu_view = False
            self.menu.update_body("Help")
            self.contents["body"] = (urwid.WidgetDisable(self.partial_view_body), None)
            self.map.draw()
            return True
        
        if _input in MenuKeyMap:
            if not self.full_menu_view:
                self.toggle_menu_view()
                return self.menu.input_handler_select_submenu(_input)
        if _input == KeyMap.CENTER_CAMERA:
            self.center_map_camera()
            return True
        
        if _input == KeyMap.CHANGE_RESOLUTION:
            self.map.change_resolution()
            self.center_map_camera()
            return True
        
        self.get_player_component(User).last_input = _input
        return True

    def handle_input(self, _input: str) -> None:
        for handler in self.input_handlers:
            if handler["callback"](_input):
                return
        
    def center_map_camera(self) -> None:
        max_y, max_x = self.mind.screen_size
        max_x -= FOOTER_HEIGHT
        if self.full_menu_view:
            max_y -= MENU_WIDTH 
        self.map.center_camera(max_x, max_y)
        self.map.draw()

    def toggle_menu_view(self) -> None:
        self.full_menu_view = not self.full_menu_view
        if self.full_menu_view:
            self.contents["body"] = (urwid.WidgetDisable(self.full_view_body), None)
        else:
            self.contents["body"] = (urwid.WidgetDisable(self.partial_view_body), None)
        self.map.draw()

class BottlesAndQuickItemFrame(Scene, urwid.Columns):
    BOTTLE_WIDTH = 8

    def __init__(self, mind) -> None:
        self.mind = mind
        self.master = mind.master
        num_of_slots = QuickItemSlots.BASE_SLOTS
        # if self.player.equipment:
        #     num_of_slots += 3
        max_num_of_slots = QuickItemSlots.MAX_SLOTS
        quick_items = []
        for i in range(max_num_of_slots):
            if i < num_of_slots:
                slot_frame = urwid.LineBox(
                    frames.ImageFrame(ImageCollection.REJUVENATION_POTION.LARGE), title=str(i + 1)
                )
            else:
                slot_frame = urwid.LineBox(frames.ImageFrame(ImageCollection.EMPTY))
            quick_items.append(slot_frame)

        self.quick_items_columns = quick_items
        self.status_walker = urwid.SimpleFocusListWalker(
            [
                urwid.Text(f""),
                urwid.Text(f""),
            ]
        )
        
        self.status_columns = [urwid.LineBox(urwid.ListBox(self.status_walker))]
        self.menu_view = self.status_columns
        super().__init__(
            mind,
            [(self.BOTTLE_WIDTH, frames.ImageFrame(ImageCollection.RED_BOTTLE.L0))]
            + [(self.BOTTLE_WIDTH + 2, frames.ImageFrame(ImageCollection.GREEN_BOTTLE.L0, x_offset=1))]
            + [(self.BOTTLE_WIDTH, frames.ImageFrame(ImageCollection.BLUE_BOTTLE.L0))]
            + self.menu_view,
        )
        self.update_red_bottle()
        self.update_blue_bottle()
        self.update_green_bottle()

        self.register_callback("player_red_changed", self.update_status_walker)
        self.register_callback("player_blue_changed", self.update_status_walker)
        self.register_callback("player_green_changed", self.update_status_walker)
        self.register_callback("player_status_changed", self.update_status_walker)
        self.register_callback("player_acting_changed", self.update_status_walker)
        self.register_callback("player_red_changed", self.update_red_bottle)
        self.register_callback("player_blue_changed", self.update_blue_bottle)
        self.register_callback("player_green_changed", self.update_green_bottle)
        self.register_callback("player_used_quick_item", self.remove_quick_item)
        self.register_callback("player_add_quick_item", self.add_quick_item)
        self.update_status_walker()

    def input_handler(self, _input: str) -> bool:
        if _input.isnumeric() and QuickItemSlots.BASE_SLOTS <= int(_input) <= QuickItemSlots.MAX_SLOTS:
            return True
        return False

    def update_status_walker(self) -> None:
        recoil = self.get_player_component(Acting).action_recoil
        max_bars = 22
        recoil_bars = max_bars - int((max_bars * recoil) // Recoil.MAX)
        self.status_walker[0].set_text(["▰" * recoil_bars, "▱" * (max_bars - recoil_bars)])
        in_loc: InLocation = self.get_player_component(InLocation)
        sight: Sight = self.get_player_component(Sight)
        sight_blocks = []
        for d in range(1, sight.radius + 1):
            block_a = max(MIN_ALPHA, 255 - int((255-MIN_ALPHA)/sight.radius * d))
            r, g, b = RGBA_to_RGB(*sight.color, block_a)
            sight_blocks.append((urwid.AttrSpec(f"#{r:02x}{g:02x}{b:02x}", ""), "█"))
        self.status_walker[1].set_text([f"{in_loc.marker}{sight.icon.value}"] + sight_blocks)

    def toggle_view(self) -> None:
        if self.menu_view == self.quick_items_columns:
            self.contents[3:] = [(c, ("weight", 1, False)) for c in self.status_columns]
            self.menu_view = self.status_columns
        else:
            self.contents[3:] = [(c, ("weight", 1, False)) for c in self.quick_items_columns]
            self.menu_view = self.quick_items_columns

    def remove_quick_item(self, slot: int) -> None:
        num_of_slots = QuickItemSlots.BASE_SLOTS
        if slot < num_of_slots:
            self.quick_items_columns.contents[slot] = urwid.LineBox(
                frames.ImageFrame(ImageCollection.EMPTY), ("weight", 1)
            )
        else:
            self.quick_items_columns.contents[slot] = (
                urwid.LineBox(frames.ImageFrame(ImageCollection.EMPTY), title=str(slot + 1)),
                ("weight", 1),
            )
        # self.emit_event("redraw_local_ui")

    def add_quick_item(self, slot: int, item_id: int) -> None:
        return
        if item.has_component(Image):
            self.quick_items_columns.contents[slot] = (
                urwid.LineBox(frames.ImageFrame(item.image), title=str(slot + 1)),
                ("weight", 1),
            )
        # self.emit_event("redraw_local_ui")

    def update_red_bottle(self) -> None:
        red = self.get_player_component(RGB).red
        red_percentage = red.value / red.max_value
        match red_percentage:
            case x if x == 1:
                red_bottle_image = ImageCollection.RED_BOTTLE.L0
            case x if x >= 0.8:
                red_bottle_image = ImageCollection.RED_BOTTLE.L1
            case x if x >= 0.6:
                red_bottle_image = ImageCollection.RED_BOTTLE.L2
            case x if x >= 0.4:
                red_bottle_image = ImageCollection.RED_BOTTLE.L3
            case x if x >= 0.2:
                red_bottle_image = ImageCollection.RED_BOTTLE.L4
            case x if x > 0:
                red_bottle_image = ImageCollection.RED_BOTTLE.L5
            case _:
                red_bottle_image = ImageCollection.RED_BOTTLE.L6

        if red_reg := self.get_player_component(RedRegeneration):
            red_reg_percentage = min(1, (red.value + red_reg.value)/ red.max_value)
            match red_reg_percentage:
                case x if x == 1:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
                case x if x >= 0.8:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L1
                case x if x >= 0.6:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L2
                case x if x >= 0.4:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L3
                case x if x >= 0.2:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L4
                case x if x > 0:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L5
                case _:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
            red_bottle_image = reg_bottle_image.surface.copy().blit(red_bottle_image.surface, (0, 0))

        self.contents[0] = (frames.ImageFrame(red_bottle_image), ("given", self.BOTTLE_WIDTH, None))
        self.emit_event("redraw_local_ui")

    def update_blue_bottle(self) -> None:
        blue = self.get_player_component(RGB).blue
        blue_percentage = blue.value / blue.max_value
        match blue_percentage:
            case x if x == 1:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L0
            case x if x >= 0.8:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L1
            case x if x >= 0.6:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L2
            case x if x >= 0.4:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L3
            case x if x >= 0.2:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L4
            case x if x > 0:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L5
            case _:
                blue_bottle_image = ImageCollection.BLUE_BOTTLE.L6
        
        if blue_reg := self.get_player_component(BlueRegeneration):
            blue_reg_percentage = min(1, (blue.value + blue_reg.value)/ blue.max_value)
            match blue_reg_percentage:
                case x if x == 1:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
                case x if x >= 0.8:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L1
                case x if x >= 0.6:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L2
                case x if x >= 0.4:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L3
                case x if x >= 0.2:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L4
                case x if x > 0:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L5
                case _:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
            blue_bottle_image = reg_bottle_image.surface.copy().blit(blue_bottle_image.surface, (0, 0))

        self.contents[2] = (frames.ImageFrame(blue_bottle_image), ("given", self.BOTTLE_WIDTH, None))
        self.emit_event("redraw_local_ui")
    
    def update_green_bottle(self) -> None:
        green = self.get_player_component(RGB).green
        green_percentage = green.value / green.max_value
        match green_percentage:
            case x if x == 1:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L0
            case x if x >= 0.8:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L1
            case x if x >= 0.6:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L2
            case x if x >= 0.4:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L3
            case x if x >= 0.2:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L4
            case x if x > 0:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L5
            case _:
                green_bottle_image = ImageCollection.GREEN_BOTTLE.L6
        
        if green_reg := self.get_player_component(GreenRegeneration):
            green_reg_percentage = min(1, (green.value + green_reg.value)/ green.max_value)
            match green_reg_percentage:
                case x if x == 1:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
                case x if x >= 0.8:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L1
                case x if x >= 0.6:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L2
                case x if x >= 0.4:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L3
                case x if x >= 0.2:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L4
                case x if x > 0:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L5
                case _:
                    reg_bottle_image = ImageCollection.REGEN_BOTTLE.L0
            green_bottle_image = reg_bottle_image.surface.copy().blit(green_bottle_image.surface, (0, 0))

        self.contents[1] = (frames.ImageFrame(green_bottle_image, x_offset=1), ("given", self.BOTTLE_WIDTH + 2, None))
        self.emit_event("redraw_local_ui")

class MapFrame(Scene, urwid.Frame):
    def __init__(self, mind):
        self.map_walker = urwid.SimpleListWalker([urwid.Text("")])
        map_box = urwid.ListBox(self.map_walker)
        self.layer_view = -1
        self.debug_view = False
        super().__init__(mind, map_box)
        self.camera_offset = (0, 0)
        self.register_callback("redraw_local_ui", self.draw, priority = 1)
        self.render_double_buffer = True
    
    def center_camera(self, max_x: int, max_y: int) -> None:
        in_location: InLocation = self.get_player_component(InLocation)
        x, y, _ = in_location.position
        if self.render_double_buffer:
            self.camera_offset = (max_y // 2-y, max_x-x)
        else:
            self.camera_offset = (max_y // 2-y, max_x // 2-x)

    def change_resolution(self) -> None:
        self.render_double_buffer = not self.render_double_buffer
        self.draw()

    def draw(self) -> None:
        in_location: InLocation = self.get_player_component(InLocation)
        sight: Sight = self.get_player_component(Sight)
        map_with_attr = [urwid.Text(line, wrap="clip") for line in render_dungeon_map(in_location, sight, self.camera_offset, self.mind.screen_size, self.render_double_buffer)]
        self.map_walker[:] = map_with_attr


class MenuFrame(Scene, urwid.Frame):
    def __init__(self, mind) -> None:
        self.bodies: dict[str, SubMenu] = {
            # "Inventory": InventoryFrame(mind),
            "Status": StatusFrame(mind),
            # "Equipment": EquipmentFrame(mind),
            "Chat": ChatFrame(mind),
            "Help": HelpFrame(mind),
            "Explorer": ExplorerFrame(mind),
            "Minimap": MinimapFrame(mind)
        }
        initial_submenu = "Help"
        self.active_body = self.bodies[initial_submenu]
        super().__init__(mind, urwid.LineBox(self.active_body, title=initial_submenu))

    def selectable(self) -> bool:
        return False

    def input_handler_full_view(self, _input: str) -> bool:
        if self.active_body.input_handler(_input):
            return True
        return self.input_handler_select_submenu(_input)

    def input_handler_select_submenu(self, _input: str) -> bool:
        if _input == KeyMap.STATUS_MENU:
            self.update_body("Status")
            return True
        elif _input == KeyMap.HELP_MENU:
            self.update_body("Help")
            return True
        elif _input == KeyMap.EXPLORER_MENU:
            self.update_body("Explorer")
            return True
        elif _input == KeyMap.CHAT_MENU:
            self.update_body("Chat")
            return True
        elif _input == KeyMap.MINIMAP_MENU:
            self.update_body("Minimap")
            return True
        return False

    def update_body(self, _title: str) -> None:
        self.active_body = self.bodies[_title]
        self.contents["body"] = (urwid.LineBox(self.active_body, title=_title), None)


class SubMenu(Scene, urwid.Pile):
    pass


class MinimapFrame(SubMenu):
    def __init__(self, mind):
        self.map_walker = urwid.SimpleListWalker([urwid.Text("")])
        map_box = urwid.ListBox(self.map_walker)
        super().__init__(mind, [map_box])
        self.register_callback("player_sight_changed", self.draw, priority = 1)
        self.draw()
    
    def draw(self) -> None:
        in_location: InLocation = self.get_player_component(InLocation)
        sight: Sight = self.get_player_component(Sight)
        map_with_attr = [urwid.Text(line, wrap="clip") for line in render_dungeon_minimap(in_location, sight)]
        self.map_walker[:] = map_with_attr

class ChatMessageAttribute(str, Enum):
    SELF = "self"
    MESSAGE = "message"
    SYSTEM = "system"
    ERROR = "error"


class ChatFrame(SubMenu):
    def __init__(self, mind, visible_lines: int = 0):
        self.log = []
        self.visible_lines = visible_lines
        self.log_widget = urwid.ListBox(urwid.SimpleListWalker([]))
        self.user_input = urwid.Text("_")
        super().__init__(mind, [self.log_widget, (4, urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker([self.user_input]))))])
        self.register_callback("chat_message_received", self.receive_chat_message)
        description:Info = self.get_player_component(Info)
        self.chat_id = self.mind.avatar.uuid.hex
        self.chat_name = f"{description.name}#{self.mind.avatar.uuid.hex[:2]}"

    def receive_chat_message(self, _from_name: str, _from_id: str, msg: str, attribute: ChatMessageAttribute, language = Language.COMMON) -> None:
        languages = self.get_player_component(Info).languages
        if language not in languages:
            msg = Language.encrypt(msg, language)
        
        if _from_id == self.chat_id:
            self.log.append(urwid.Text(("green", f"Me: {msg}")))
        elif attribute == ChatMessageAttribute.SYSTEM:
            self.log.append(urwid.Text(("cyan", f"{_from_name}: {msg}")))
        elif attribute == ChatMessageAttribute.ERROR:
            self.log.append(urwid.Text(("red", f"{_from_name}: {msg}")))
        elif attribute == ChatMessageAttribute.MESSAGE:
            self.log.append(urwid.Text(f"{_from_name}: {msg}"))

        if self.visible_lines == 0:
            self.visible_lines = max(self.mind.screen_size[1] - FOOTER_HEIGHT - 2, 1)
        elif isinstance(self.visible_lines, int):
            self.visible_lines = max(self.visible_lines, 1)
        self.log_widget.body[:] = self.log[-self.visible_lines :]
        self.emit_event("redraw_local_ui")
    
    def send_chat_message(self) -> None:
        msg: str = self.user_input.get_text()[0].strip()[:-1]
        if msg.strip():
            description:Info = self.get_player_component(Info)
            if not description.languages:
                self.receive_chat_message("System", self.chat_id, "You don't know any languages!", ChatMessageAttribute.ERROR)
                return
            
            self.emit_event("chat_message_sent", self.chat_name, self.chat_id, msg, ChatMessageAttribute.MESSAGE, description.languages[0])
        self.user_input.set_text("_")
    
    def input_handler(self, _input: str) -> bool:
        if _input == ChatKeyMap.SEND:
            self.send_chat_message()
        elif _input == ChatKeyMap.DELETE:
            self.user_input.set_text(self.user_input.get_text()[0][:-2] + "_")
        elif _input == ChatKeyMap.CLEAR:
            self.user_input.set_text("_")
        elif len(_input) == 1:
            self.user_input.set_text(self.user_input.get_text()[0][:-1] + _input + "_")
        else:
            return False
        return True

class LogFrame(SubMenu):
    def __init__(self, mind, visible_lines: int = 0):
        self.log = []
        self.visible_lines = visible_lines
        self.log_widget = urwid.ListBox(urwid.SimpleListWalker([]))
        super().__init__(mind, [self.log_widget])
        self.register_callback("log", self.update_log)

    def update_log(self, _log):
        self.log.append(_log)
        if self.visible_lines == 0:
            self.visible_lines = max(self.mind.screen_size[1] - FOOTER_HEIGHT - 2, 1)
        elif isinstance(self.visible_lines, int):
            self.visible_lines = max(self.visible_lines, 1)
        self.log_widget.body[:] = self.log[-self.visible_lines :]


class InventoryFrame(SubMenu):
    def __init__(self, mind):
        columns = urwid.Columns([urwid.Text("")])
        box = urwid.ListBox(urwid.SimpleListWalker([columns]))
        self.box = box.body
        self.default_header = urwid.Text("0/9-= to select\n\n", align="center")
        self.default_footer = urwid.Text([("green", f"{'Enter:use/eqp':<14s}"), ("yellow", "Q:drop")], align="center")
        super().__init__(mind, box, header=self.default_header, footer=self.default_footer)

    @property
    def selection_data(self):
        if not self.player.inventory.selection:
            return urwid.Text("")
        i = self.player.inventory.selection
        _text = []
        _text += [i.eq_description, f"\nEncumbrance:{i.encumbrance}\n"]
        return urwid.Text(_text)

    def update_header(self):
        if not self.player.inventory.selection:
            self.contents["header"] = (self.default_header, None)
        else:
            i = self.player.inventory.selection
            self.contents["header"] = (
                urwid.Text([(i.color, f"{i.name}\n"), f"{i.description}\n"], align="center"),
                None,
            )

    def update_footer(self):
        if not self.player.inventory.selection:
            self.contents["footer"] = (self.default_footer, None)
        else:
            i = self.player.inventory.selection
            _text = []
            if not i.requisites(self.player):
                _text += [("red", f"{'Cannot equip':<14s}")]
            elif not i.is_equipped:
                _text += [("green", f"{'Enter:equip':<14s}")]
            elif i.is_equipped:
                _text += [("green", f"{'Enter:unequip':<14s}")]
            elif i.is_consumable:
                _text += [("green", f"{'Enter:use':<14s}")]
            _text += [("yellow", "Q:drop")]
            self.contents["footer"] = (urwid.Text(_text, align="center"), None)

    def update_body(self):
        side = urwid.Text("║")
        width = 8
        height = 6

        _marker_box = ["╔" + "═" * width + "╗\n"]
        for x in range(height):
            _marker_box += ["║"]
            for y in range(width):
                _marker_box += ["."]
            _marker_box += ["║\n"]
        _marker_box += ["╚" + "═" * width + "╝"]
        if self.player.inventory.selection:
            i = self.player.inventory.selection
            X_OFFSET = 2
            Y_OFFSET = 4
            for m, pos in zip(i.in_inventory_markers, i.in_inventory_marker_positions):
                x, y = pos
                _marker_box[(x + X_OFFSET) * (width + 2) + y + Y_OFFSET] = (i.color, m)
        self.box[:] = [
            urwid.Columns(
                [(width + 2, urwid.Text(_marker_box)), self.selection_data],
                dividechars=1,
            )
        ]


class StatusFrame(SubMenu):
    def __init__(self, mind):
        self.description_walker = urwid.SimpleListWalker([urwid.Text("")])
        super().__init__(mind, [(IMAGE_MAX_HEIGHT, EMPTY_FILL), urwid.ListBox(self.description_walker)])

        self.register_callback("new_player", self.update_player_image)
        self.register_callback("player_equip", self.update_player_image)
        self.register_callback("player_unequip", self.update_player_image)
        self.register_callback("player_image_changed", self.update_player_image, priority=1)
        self.register_callback("player_movement", self.update_info)
        self.register_callback("player_status_changed", self.update_info)
        self.register_callback("player_red_changed", self.update_info)
        self.register_callback("player_green_changed", self.update_info)
        self.register_callback("player_blue_changed", self.update_info)
        self.update_info()
        self.update_player_image()

    def update_player_image(self):
        bkg_surface = ImageCollection.BACKGROUND_NONE.surface.copy()
        img: Image = self.get_player_component(Image)
        # round to nearest int: (n + d // 2) // d
        x_offset = (bkg_surface.get_width() - img.surface.get_width() + 1)//2
        y_offset = bkg_surface.get_height() - img.surface.get_height()
        bkg_surface.blit(img.surface, (x_offset, y_offset))
        self.contents[0] = (frames.ImageFrame(Image(bkg_surface)), ("given", IMAGE_MAX_HEIGHT))
        self.emit_event("redraw_local_ui")

    def update_info(self) -> None:
        def color(char: int) -> tuple[str, str]:
            if char <= 6:
                return ("red", f"{char:02d}")
            elif char <= 9:
                return ("yellow", f"{char:02d}")
            elif char <= 12:
                return ("white", f"{char:02d}")
            elif char <= 16:
                return ("green", f"{char:02d}")
            else:
                return ("cyan", f"{char:02d}")

        
        in_loc: InLocation = self.get_player_component(InLocation)
        x, y, _ = in_loc.position
        info: Info = self.get_player_component(Info)
        rgb: RGB = self.get_player_component(RGB)
        # primary_color = f"{hex(rgb.red.value)[2:]}{hex(rgb.green.value)[2:]}{hex(rgb.blue.value)[2:]}"
        self.description_walker[:] = [
            urwid.Text(f"{info.name:<10s} {info.game_class} @({y},{x})"),
            urwid.Text(f"  RED:{rgb.red.value:03d} GRN:{rgb.green.value:03d} BLU:{rgb.blue.value:03d}"),
            urwid.Text(["  STR:", color(rgb.strength), "  DEX:", color(rgb.dexterity), "  ACU:", color(rgb.acumen)]),
            # urwid.Text(", ".join(info.languages)),
        ]
        
class ExplorerFrame(SubMenu):
    NO_TARGET_TEXT = "There's no one around. ".center(MENU_WIDTH)
    def __init__(self, mind):
        self.description_walker = urwid.SimpleListWalker([urwid.Text(self.NO_TARGET_TEXT)])
        super().__init__(mind, [(IMAGE_MAX_HEIGHT, EMPTY_FILL), urwid.ListBox(self.description_walker)])

        self.target = None
        self.register_callback("redraw_local_ui", self.update_target)
        self.register_callback("other_player_image_changed", self.update_target_image)
        self.register_callback("other_player_info_changed", self.update_target_info)

        self.update_target()
        self.nearest_index = 0
        self.nearby_entities = []

    def update_target(self) -> None:
        self.nearby_entities = self.nearby_entities_list()
        target = self.nearby_entities[0] if self.nearby_entities else None
        if target is not self.target:
            self.target = target
            self.update_target_info()
            self.update_target_image()
    
    def input_handler(self, _input: str) -> bool:
        if _input not in (ExplorerKeyMap.NEXT, ExplorerKeyMap.PREVIOUS):
            return False
        if not self.nearby_entities:
            return True
        if _input == ExplorerKeyMap.NEXT:
            self.nearest_index = (self.nearest_index + 1) % len(self.nearby_entities)
        elif _input == ExplorerKeyMap.PREVIOUS:
            self.nearest_index = (self.nearest_index - 1) % len(self.nearby_entities)
        
        target = self.nearby_entities[self.nearest_index]
        if target is not self.target:
            self.target = target
            self.update_target_info()
            self.update_target_image()
        return True
    

    def nearby_entities_list(self) -> list[int]:
        in_location: InLocation = self.get_player_component(InLocation)
        sight: Sight = self.get_player_component(Sight)

        entities = []
        # entities will be sorted by distance because visible tiles is sorted by distance.
        for x, y in sight.visible_tiles:
            for z in (1, 0, 2): #first creatures layer, than items, than flyers
                if ent_id := in_location.dungeon.get_at((x, y, z)):
                    if ent_id != self.player_id and self.world.try_component(ent_id, Info):
                        entities.append(ent_id)
        return entities

    def update_target_image(self) -> None:
        if not self.target:
            self.contents[0] = (EMPTY_FILL, ("given", IMAGE_MAX_HEIGHT))
            return
        
        img = self.world.try_component(self.target, Image)
        if not img:
            self.contents[0] = (EMPTY_FILL, ("given", IMAGE_MAX_HEIGHT))
            return

        bkg_surface = ImageCollection.BACKGROUND_NONE.surface.copy()
        # round to nearest int: (n + d // 2) // d
        x_offset = (bkg_surface.get_width() - img.surface.get_width() + 1)//2
        y_offset = bkg_surface.get_height() - img.surface.get_height()
        bkg_surface.blit(img.surface, (x_offset, y_offset))
        self.contents[0] = (frames.ImageFrame(Image(bkg_surface)), ("given", IMAGE_MAX_HEIGHT))

    def update_target_info(self) -> None:
        if not self.target:
            self.description_walker[:] = [urwid.Text(self.NO_TARGET_TEXT)]
            return

        info: Info = self.world.try_component(self.target, Info)
        if not info:
            self.description_walker[:] = [urwid.Text("A mysterious entity.")]
            return

        x, y, _ = self.world.try_component(self.target, InLocation).position
        description_walker = [
            urwid.Text(f"{info.name:<10s} {info.game_class} @({x},{y})")
        ]
        # color_descriptor: ColorDescriptor = self.world.try_component(self.target, ColorDescriptor)
        # if color_descriptor:
        #     description_walker.append(urwid.Text(color_descriptor.hex()))
        # else:
        #     description_walker.append(urwid.Text("No color descriptor."))
        self.description_walker[:] = description_walker


class EquipmentFrame(SubMenu):
    def __init__(self, mind):
        box = EMPTY_FILL
        self.box = box.body
        super().__init__(mind, box)

    def on_update(self) -> None:
        player = self.player

        _equipment = []
        for t, obj in player.equipment.items():
            _name = t.replace("_", " ")
            _name = _name[0].upper() + _name[1:]
            if obj:
                _equipment += [urwid.Text([f"{_name}: ", (obj.color, f"{obj.name}")])]
            else:
                _equipment += [urwid.Text([f"{_name}: "])]

        _bonus = {}
        for eqp in player.equipment_set:
            for b in set(list(eqp.bonus.keys()) + list(eqp.set_bonus.keys())):
                val = player.full_eqp_bonus(eqp, b)
                if b not in _bonus:
                    _bonus[b] = val
                else:
                    _bonus[b] += val

        _top = ""
        for b, val in _bonus.items():
            if b == "dmg_reduction":
                _top += f"Reduction:{val} "
            else:
                _top += f"{b}:{val} "
        _top += "\n"
        self.box[:] = [urwid.Text(_top)] + _equipment


class HelpFrame(SubMenu):
    def __init__(self, mind):
        self.mind = mind
        self.master = mind.master
        map_commands = [
            ("cyan", "Map commands"),
            f"←→↑↓: move",
            f"c: center camera"
        ]
        player_commands = [("green", "\nPlayer commands")]

        # class_action_keys = [k for k in KeyMap]
        _acting: Acting = self.get_player_component(Acting)
        for i, act in _acting.actions.items():
            if not act.description.lower().startswith("move"):
                player_commands.append(f"{i}: {act.description.lower()}")
        menu_commands = [
            ("red", "\nMenu commands"),
            f"tab: open/close",
            f"S: status",
            f"H: help",
            f"X: explorer",
            f"C: chat",
            f"M: map",
        ]
        
        super().__init__(mind, [
            urwid.ListBox(urwid.SimpleListWalker(
                [urwid.Text(text, wrap="clip") for text in map_commands + player_commands + menu_commands]
            ))
        ])


CHARACTERS_SELECTION_FRAMES = {
    GenderType.FEMALE: {
        "none": {k: None for k in CharacterSelectionFrame.options},
        "selected": {k: None for k in CharacterSelectionFrame.options},
        "unselected": {k: None for k in CharacterSelectionFrame.options},
    },
    GenderType.MALE: {
        "none": {k: None for k in CharacterSelectionFrame.options},
        "selected": {k: None for k in CharacterSelectionFrame.options},
        "unselected": {k: None for k in CharacterSelectionFrame.options},
    },
}

for c in CharacterSelectionFrame.options:
    for gender in GenderType:
        for bkg in ("none", "unselected", "selected"):
            if bkg == "none":
                bkg_surface = ImageCollection.BACKGROUND_NONE.surface.copy()
            elif bkg == "selected":
                bkg_surface = ImageCollection.BACKGROUND_SELECTED.surface.copy()
            else:
                bkg_surface = ImageCollection.BACKGROUND_NONE.surface.copy()
            char_img = ImageCollection.CHARACTERS[gender][c].surface
            x_offset = (bkg_surface.get_width() - char_img.get_width()) // 2
            y_offset = bkg_surface.get_height() - char_img.get_height()
            bkg_surface.blit(char_img, (x_offset, y_offset))
            CHARACTERS_SELECTION_FRAMES[gender][bkg][c] = frames.ImageFrame(Image(bkg_surface))
