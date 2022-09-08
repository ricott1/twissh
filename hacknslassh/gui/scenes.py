# encoding: utf-8

from typing import Callable
import urwid
import copy
from hacknslassh.utils import distance
from ..gui import frames
from .utils import SelectableColumns, attr_button, SelectableListBox
from ..components import Entity, Image, ImageCollection, GenderType, QuickItemSlots
from hacknslassh.constants import *
from urwid import raw_display

SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()

MIN_HEADER_HEIGHT = 3
MAX_MENU_WIDTH = 48
FOOTER_HEIGHT = 4

PALETTE = [
    ("line", "black", "white", "standout"),
    ("top", "white", "black"),
    ("frame", "white", "white"),
    ("player", "light green", "black"),
    ("other", "light blue", "black"),
    ("monster", "dark red", "black"),
    ("fatigued", "dark red", "white", "standout"),
    ("reversed", "standout", ""),
    ("common", "white", "black"),
    ("common_line", "black", "white", "standout"),
    ("uncommon", "dark cyan", "black"),
    ("uncommon_line", "dark cyan", "white", "standout"),
    ("rare", "yellow", "black"),
    ("rare_line", "yellow", "white", "standout"),
    ("unique", "light magenta", "black"),
    ("unique_line", "light magenta", "white", "standout"),
    ("set", "light green", "black"),
    ("set_line", "light green", "white", "standout"),
    ("normal", "white", "black"),
    ("positive", "light green", "black"),
    ("negative", "dark red", "black"),
    ("white", "white", "black"),
    ("disabled", "dark red", "black"),
    ("red", "dark red", "black"),
    ("green", "light green", "black"),
    ("yellow", "yellow", "black"),
    ("brown", "brown", "black"),
    ("white_line", "black", "white", "standout"),
    ("red_line", "dark red", "white", "standout"),
    ("green_line", "light green", "white", "standout"),
    ("yellow_line", "yellow", "white", "standout"),
    ("cyan", "light cyan", "black"),
    ("cyan_line", "light cyan", "white", "standout"),
    ("name", "white", "black"),
]


class Scene(object):
    def __init__(self, mind, *args, palette=None, **kwargs):
        # mixin class for frame and scene properties
        self.palette = palette
        super().__init__(*args, **kwargs)
        self.mind = mind
        self.master = self.mind.master

    @property
    def player(self):
        if self.mind.avatar.uuid in self.mind.master.players:
            return self.mind.master.players[self.mind.avatar.uuid]
        else:
            return None

    def handle_input(self, _input: str) -> None:
        pass

    def on_update(self, deltatime: float) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def restart(self) -> None:
        pass

    def initialize(self, master_scene) -> None:
        pass

    def on_complete(self, master_scene) -> None:
        pass

    def register_callback(self, event_name: str, callback: Callable) -> None:
        self.mind.register_callback(event_name, callback)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        self.mind.emit_event(event_name, *args, **kwargs)


class GUI(Scene, urwid.Frame):
    def __init__(self, mind):
        self.active_body = CharacterSelectionFrame(mind)
        super().__init__(mind, self.active_body)
        self.palette = PALETTE
        self.register_callback("new_player", self.start_game_frame)

    def on_update(self, deltatime: float) -> None:
        self.active_body.on_update(deltatime)

    def handle_input(self, _input):
        self.active_body.handle_input(_input)

    # def exit(self):
    #     self.disconnect()
    #     self.mind.disconnect()#should use dispatch event

    # def restart(self):
    #     self.update_body("Intro", no_title=True)

    def start_game_frame(self):
        self.active_body = NetHackFrame(self.mind)
        self.contents["body"] = (self.active_body, None)


class CharacterSelectionFrame(Scene, urwid.Pile):
    options = {
        "Nerd": {
            "description": "Beware their nerdy glasses and their nerdy ways.",
            "bonus": "Strength +1, Hit points +4",
            "abilities": "Charge and parry",
        },
        "Bard": {
            "description": "Tell them a story and they'll sing you a song.",
            "bonus": "Strength +1, Constitution +1, Hit points +6",
            "abilities": "Demolish and parry",
        },
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
        # self.menu = frames.VerticalSelectionFrame([f"<--   {k:^7s}   --> " for k in self.options])

        max_width = max([len(opt) for opt in self.options], default=1)
        self.buttons = [
            attr_button(
                opt.center(max_width),
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
        # descriptions = urwid.WidgetDisable(urwid.ListBox(self.menu_walker))
        self.menu = urwid.ListBox(self.menu_walker)

        self.main = urwid.Columns(
            [(20, left_img), self.menu, (20, right_img)], focus_column=self.column_index, min_width=20
        )

        super().__init__(mind, [(4, self.title), self.main], focus_item=1)

    def handle_input(self, _input, pressed_since=0):
        if _input == "enter":
            row_index = self.menu.focus_position
            column_index = self.main.focus_position
            selection = self.options_keys[row_index]
            gender = GenderType.FEMALE if column_index == 0 else GenderType.MALE
            player = self.mind.master.register_new_player(self.mind.avatar.uuid, selection, gender)
            self.emit_event("new_player")

    def on_update(self, deltatime: float) -> None:
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
            self.emit_event("gui_redraw")


class NetHackFrame(Scene, urwid.Frame):
    def __init__(self, mind) -> None:
        self.map = MapFrame(mind)
        self.menu = MenuFrame(mind)
        self.bottom_menu = BottlesAndQuickItemFrame(mind)
        self.log = LogFrame(mind, visible_lines=FOOTER_HEIGHT)

        self.left = urwid.Pile([self.map, (FOOTER_HEIGHT, self.bottom_menu)])
        self.right = self.menu

        self.bottom = urwid.Columns([urwid.WidgetDisable(self.bottom_menu), (30, urwid.WidgetDisable(self.log))])
        self.full_view_body = urwid.Columns([self.left, (30, self.menu)])
        self.partial_view_body = urwid.Pile([self.map, (FOOTER_HEIGHT, self.bottom)])
        super().__init__(mind, self.full_view_body)
        self.full_menu_view = True

    def handle_input(self, _input: str) -> None:
        print(_input)
        if _input.isnumeric() and 1 <= int(_input) <= 5:
            self.bottom_menu.handle_input(_input)
        elif _input == KeyMap.TOGGLE_FULL_MENU:
            self.toggle_menu_view()
        elif _input == KeyMap.QUICK_MENU:
            self.bottom_menu.toggle_view()
        elif _input in MenuKeyMap:
            self.menu.handle_input(_input)
        else:
            self.map.handle_input(_input)

    def toggle_menu_view(self) -> None:
        self.full_menu_view = not self.full_menu_view
        if self.full_menu_view:
            self.contents["body"] = (self.full_view_body, None)
        else:
            self.contents["body"] = (self.partial_view_body, None)
        self.emit_event("gui_redraw")

    def on_update(self, deltatime: float) -> None:
        self.map.on_update(deltatime)
        self.log.on_update(deltatime)
        if self.full_menu_view:
            self.menu.on_update(deltatime)


class BottlesAndQuickItemFrame(Scene, urwid.Columns):
    BOTTLE_WIDTH = 10

    def __init__(self, mind) -> None:
        self.mind = mind
        num_of_slots = QuickItemSlots.BASE_SLOTS
        # if self.player.equipment:
        #     num_of_slots += 3
        max_num_of_slots = QuickItemSlots.MAX_SLOTS
        quick_items = []
        for i in range(max_num_of_slots):
            if i < num_of_slots:
                slot_frame = urwid.LineBox(
                    frames.ImageFrame(ImageCollection.REJUVENATION_POTION.MEDIUM), title=str(i + 1)
                )
            else:
                slot_frame = urwid.LineBox(frames.ImageFrame(ImageCollection.EMPTY))
            quick_items.append(slot_frame)

        self.quick_items_columns = quick_items
        hp = self.player.health
        mp = self.player.mana
        self.status_walker = urwid.SimpleFocusListWalker(
            [
                urwid.Text(f"HP: {hp.value}/{hp.max_value}  MP: {mp.value}/{mp.max_value}"),
                urwid.Text(f"Class L: Experiencebars"),
            ]
        )
        self.status_columns = [urwid.LineBox(urwid.ListBox(self.status_walker))]
        self.menu_view = self.status_columns
        super().__init__(
            mind,
            [(self.BOTTLE_WIDTH, frames.ImageFrame(ImageCollection.HP_BOTTLE.L0, x_offset=1))]
            + self.menu_view
            + [(self.BOTTLE_WIDTH, frames.ImageFrame(ImageCollection.MP_BOTTLE.L0, x_offset=1))],
        )
        self.register_callback("player_hp_changed", self.update_hp_bottle)
        self.register_callback("player_mp_changed", self.update_mp_bottle)
        self.register_callback("player_used_quick_item", self.remove_quick_item)
        self.register_callback("player_add_quick_item", self.add_quick_item)

    def handle_input(self, _input: str) -> None:
        self.player.use_quick_item(int(_input))

    def toggle_view(self) -> None:
        if self.menu_view == self.quick_items_columns:
            self.contents[1:-1] = [(c, ("weight", 1, False)) for c in self.status_columns]
            self.menu_view = self.status_columns
        else:
            self.contents[1:-1] = [(c, ("weight", 1, False)) for c in self.quick_items_columns]
            self.menu_view = self.quick_items_columns
        self.emit_event("gui_redraw")

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
        self.emit_event("gui_redraw")

    def add_quick_item(self, slot: int, item: Entity) -> None:
        if item.has_component(Image):
            self.quick_items_columns.contents[slot] = (
                urwid.LineBox(frames.ImageFrame(item.image), title=str(slot + 1)),
                ("weight", 1),
            )
        self.emit_event("gui_redraw")

    def update_hp_bottle(self) -> None:
        hp_percentage = self.player.hp / self.player.max_hp
        match hp_percentage:
            case x if x == 1:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L0
            case x if x >= 0.8:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L1
            case x if x >= 0.6:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L2
            case x if x >= 0.4:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L3
            case x if x >= 0.2:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L4
            case x if x > 0:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L5
            case _:
                hp_bottle_image = ImageCollection.HP_BOTTLE.L6
        self.contents[0] = (frames.ImageFrame(hp_bottle_image, x_offset=1), ("given", self.BOTTLE_WIDTH))
        self.emit_event("gui_redraw")

    def update_mp_bottle(self) -> None:
        mp_percentage = self.player.mp / self.player.max_mp
        match mp_percentage:
            case x if x == 1:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L0
            case x if x >= 0.8:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L1
            case x if x >= 0.6:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L2
            case x if x >= 0.4:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L3
            case x if x >= 0.2:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L4
            case x if x > 0:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L5
            case _:
                mp_bottle_image = ImageCollection.MP_BOTTLE.L6
        self.contents[-1] = (frames.ImageFrame(mp_bottle_image, x_offset=1), ("given", self.BOTTLE_WIDTH))
        self.emit_event("tui_updated")


class GameFrame(Scene, urwid.Frame):
    def __init__(self, mind):
        self.mind = mind

        _header = urwid.LineBox(
            urwid.BoxAdapter(
                SelectableListBox(urwid.SimpleFocusListWalker([urwid.Text("")])),
                self.header_height,
            )
        )

        self._menu_view = True
        self.map = MapFrame(self, mind)
        self.menu = MenuFrame(self, mind)

        super().__init__(
            mind,
            urwid.Columns(
                [(self.map_width, self.map), (self.menu_width, self.menu)],
                focus_column=1,
            ),
            header=_header,
            footer=None,
            focus_part="body",
        )

        self.update_footer()
        self.header_widget = self.header.original_widget.box_widget
        self.footer_content_size = 0

    @property
    def header_height(self):
        return MIN_HEADER_HEIGHT  # max(MIN_HEADER_HEIGHT, self.mind.screen_size[1]//8)

    @property
    def menu_width(self):
        if self.menu_view:
            return min(MAX_MENU_WIDTH, (3 * self.mind.screen_size[0]) // 7)
        return 0

    @property
    def map_width(self):
        if self.menu_view:
            return self.mind.screen_size[0] - self.menu_width
        return self.mind.screen_size[0]

    @property
    def menu_view(self):
        return self._menu_view

    @menu_view.setter
    def menu_view(self, value):
        self._menu_view = value
        _columns = [(self.map_width, self.map), (self.menu_width, self.menu)]
        self.contents["body"] = (urwid.Columns(_columns, focus_column=1), None)

    @property
    def header_list(self):
        return sorted(
            [
                ent
                for k, ent in self.player.location.entities.items()
                if distance(self.player.position, ent.position) <= 3 and ent.status
            ],
            key=lambda ent: distance(self.player.position, ent.position),
        )

    def update_footer(self):
        _size = 0
        inv_btns = []
        for i, obj in self.player.inventory.content.items():
            if obj:
                _size += 1
                if obj.is_equipment and obj.is_equipped:
                    _marker = ["[", (obj.color, f"{obj.marker[0]}"), "]"]
                elif obj.is_equipment and not obj.is_equipped:
                    _marker = ["]", (obj.color, f"{obj.marker[0]}"), "["]
                elif obj.is_consumable:
                    _marker = ["(", (obj.color, f"{obj.marker[0]}"), ")"]
                else:
                    _marker = [f" {obj.marker[0]} "]
            else:
                _marker = [f"  "]
            if i < 9:
                _num = f"\n {i+1} "
            elif i == 9:
                _num = "\n 0 "
            elif i == 10:
                _num = "\n - "
            elif i == 11:
                _num = "\n = "
            if obj and obj is self.player.inventory.selection:
                _marker += [("line", _num)]
            else:
                _marker += [("top", _num)]
            btn = urwid.Text(_marker, align="center")
            inv_btns.append((5, urwid.LineBox(btn)))

        if self.mind.screen_size != (80, 24):
            inv_btns.append(urwid.Text("\nSET TERMINAL\nTO 80X24", align="center"))

        self.contents["footer"] = (SelectableColumns(inv_btns, dividechars=0), None)
        self.footer_content_size = _size

    def on_update(self, deltatime: float) -> None:
        self.update_header()
        if self.footer_content_size != len(self.player.inventory.all):
            self.update_footer()
        if self.mind.screen_size != (80, 24):
            self.update_footer()
        self.map.on_update(deltatime)
        if self.menu_view:
            self.menu.on_update(deltatime)

    def handle_input(self, _input):
        if _input == "tab":
            self.menu_view = not self.menu_view
        elif _input == "enter" and self.player.inventory.selection:
            self.player.use_quick_item(self.player.inventory.selection)
            self.update_footer()
        elif _input == "Q" and self.player.inventory.selection:
            self.player.actions["drop"].use(self.player, obj=self.player.inventory.selection)
            self.update_footer()
        elif _input.isnumeric() or _input in ("-", "="):
            self.select_item(_input)
            self.update_footer()
        elif _input == KeyMap["status-menu"] and self.menu_view:
            self.menu.update_body("Status")
        elif _input == KeyMap["help-menu"] and self.menu_view:
            self.menu.update_body("Help")
        elif _input == KeyMap["equipment-menu"] and self.menu_view:
            self.menu.update_body("Equipment")
        elif _input == KeyMap["inventory-menu"] and self.menu_view:
            self.menu.update_body("Inventory")
        else:
            self.map.handle_input(_input)

    def select_item(self, _input):
        if _input.isnumeric() and int(_input) > 0:
            _input = int(_input) - 1
        elif _input == "0":
            s_input = 9
        elif _input == "-":
            _input = 10
        elif _input == "=":
            _input = 11
        self.player.inventory.selection = self.player.inventory.get(_input)

    def update_header(self):
        widgets = []
        for p in self.header_list:
            widgets.append(
                urwid.AttrMap(
                    urwid.AttrMap(urwid.Text(p.status, wrap="clip"), {self.player.id: "player"}),
                    {p.id: "other" for i, p in self.mind.master.players.items()},
                )
            )
        if widgets:
            self.header_widget.body[:] = widgets


class MapFrame(Scene, urwid.Frame):
    def __init__(self, mind):
        map_box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.map_box = map_box.body
        self.layer_view = -1
        self.debug_view = False
        super().__init__(mind, map_box)
        self.on_update(0)

    def on_update(self, deltatime: float) -> None:
        return
        if self.layer_view == -1:
            _map = copy.deepcopy(self.player.location.map)
        else:
            _map = self.player.location.layer_from_entities(self.layer_view, self.debug_view)

        # x, y, z = self.player.position
        # body_width = self.mind.screen_size[0]
        # w = max(0, y - body_width // 3)
        # visible_map = [line[w : w + body_width] for line in _map]
        # h = max(0, x - self.parent.body_height // 2)
        # if h + self.parent.body_height >= len(visible_map):
        #     visible_map = visible_map[len(visible_map) - self.parent.body_height :]
        # else:
        #     visible_map = visible_map[h : h + self.parent.body_height]
        visible_map = _map

        map_with_attr = [
            urwid.AttrMap(
                urwid.AttrMap(urwid.Text(line, wrap="clip"), {self.player.id: "player"}),
                {p.id: "other" for i, p in self.mind.master.players.items()},
            )
            for line in visible_map
        ]
        self.map_box[:] = map_with_attr

    def handle_input(self, _input):
        # if _input == "ctrl f":
        #     self.debug_view = not self.debug_view
        # elif _input == "ctrl v":
        #     self.layer_view = self.layer_view + 1
        #     if self.layer_view > 2:
        #         self.layer_view = -1
        # elif _input in KeyMap:
        #     _action = KeyMap[_input]
        #     self.player.handle_input(_action)
        pass


class MenuFrame(Scene, urwid.Frame):
    def __init__(self, mind):
        self.bodies = {
            # "Inventory": InventoryFrame(mind),
            "Status": StatusFrame(mind),
            # "Equipment": EquipmentFrame(mind),
            "Help": HelpFrame(mind),
            "Explorer": ExplorerFrame(mind),
        }
        initial_submenu = "Help"
        self.active_body = self.bodies[initial_submenu]
        super().__init__(mind, urwid.LineBox(self.active_body, title=initial_submenu))

    def selectable(self):
        return False

    def on_update(self, deltatime: float) -> None:
        self.active_body.on_update(deltatime)

    def handle_input(self, _input: str) -> None:
        if _input == KeyMap.STATUS_MENU:
            self.update_body("Status")
        elif _input == KeyMap.HELP_MENU:
            self.update_body("Help")
        elif _input == KeyMap.EXPLORER_MENU:
            self.update_body("Explorer")

    def update_body(self, _title):
        self.active_body = self.bodies[_title]
        self.contents["body"] = (urwid.LineBox(self.active_body, title=_title), None)


class SubMenuFrame(Scene, urwid.Frame):
    pass


class LogFrame(Scene, urwid.Frame):
    def __init__(self, mind, visible_lines: int = 0):
        self.log = []
        self.visible_lines = visible_lines
        self.log_widget = urwid.ListBox(urwid.SimpleListWalker([]))
        super().__init__(mind, self.log_widget)
        self.register_callback("log", self.update_log)

    def on_update(self, deltatime: float) -> None:
        if self.visible_lines == 0:
            self.visible_lines = max(self.mind.screen_size[1] - FOOTER_HEIGHT - 2, 1)
        elif isinstance(self.visible_lines, int):
            self.visible_lines = max(self.visible_lines, 1)
        self.log_widget.body[:] = self.log[-self.visible_lines :]

    def update_log(self, _log):
        self.log.append(_log)


class InventoryFrame(SubMenuFrame):
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

    def on_update(self, deltatime: float) -> None:
        self.update_header()
        self.update_body()
        self.update_footer()


class StatusFrame(SubMenuFrame):
    def __init__(self, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        super().__init__(mind, box)
        self.register_callback("new_player", self.update_player_image)
        self.register_callback("player_equip", self.update_player_image)
        self.register_callback("player_unequip", self.update_player_image)

    def update_player_image(self):
        self.contents["body"] = (frames.ImageFrame(self.player.image), None)

    def on_update(self, deltatime: float) -> None:
        return
        player = self.player
        x, y, z = player.position
        _top = f"{player.name:<12s} {player.game_class.name:<10s}\nLev:{player.level:<2d} Exp:{player.exp:<4d} {player.location.name}@({x},{y})\n"

        _left = []

        for s in CHARACTERISTICS:
            c = getattr(player, s)
            state = ["normal", "positive", "negative"][-int(c.temp_bonus < 0) + int(c.temp_bonus > 0)]
            menu_width = 30
            if menu_width > 40:
                _name = c.name[0].upper() + c.name[1:]
                _left += [
                    f"{_name:<12} ",
                    (state, f"{c.value:>2d}"),
                    f" ({c.mod:<+2d})\n",
                ]
            elif menu_width > 36:
                _name = c.name[0].upper() + c.name[1:6]
                _left += [
                    f"{_name:<6} ",
                    (state, f"{c.value:>2d}"),
                    f" ({c.mod:<+2d})\n",
                ]
            else:
                _left += [f"{s:<3} ", (state, f"{c.value:>2d}"), f" ({c.mod:<+2d})\n"]

        _right = []
        base = player.STR.mod
        weapon = player.equipment["main_hand"]

        if not weapon:
            min_dmg, max_dmg = (1, 4)
        else:
            number, value = weapon.dmg
            min_dmg, max_dmg = (number * 1, number * value)
        min_dmg = max(1, base + min_dmg)
        max_dmg = max(1, base + max_dmg)
        _right.append(f"Damage {min_dmg:>3d}-{max_dmg:<3d}\n")
        _right.append(f"Reduction {player.dmg_reduction:<3d}\n")
        _right.append(f"Encumb ")
        if player.inventory.encumbrance == EXTRA_ENCUMBRANCE_MULTI * player.encumbrance:
            _right.append(("red", f"{player.inventory.encumbrance:>2d}"))
        elif player.inventory.encumbrance > player.encumbrance:
            _right.append(("yellow", f"{player.inventory.encumbrance:>2d}"))
        else:
            _right.append(("white", f"{player.inventory.encumbrance:>2d}"))
        _right.append(f"/{player.encumbrance:<2d}\n")
        _right.append(f"Speed {player.movement_speed}\n")
        _right.append(f"Monsterized {player.MP:<2d}\n")

        self.box[:] = [
            urwid.Text(_top),
            urwid.Columns([urwid.Text(_left), urwid.Text(_right)], dividechars=1),
        ]


class ExplorerFrame(SubMenuFrame):
    def __init__(self, mind):
        body = frames.ImageFrame(ImageCollection.EMPTY)
        self.nearby_entities_walker = urwid.SimpleFocusListWalker([urwid.Text("")])
        footer = (SelectableListBox(self.nearby_entities_walker),)
        super().__init__(mind, body, footer=footer)

    @property
    def nearby_entities_list(self):
        return []
        return sorted(
            [
                ent
                for k, ent in self.player.location.entities.items()
                if distance(self.player.position, ent.position) <= 3 and ent.status
            ],
            key=lambda ent: distance(self.player.position, ent.position),
        )

    def on_update(self, deltatime: float) -> None:
        self.update_footer()

    def update_footer(self):
        widgets = []
        for p in self.nearby_entities_list:
            widgets.append(
                urwid.AttrMap(
                    urwid.AttrMap(urwid.Text(p.status, wrap="clip"), {self.player.id: "player"}),
                    {p.id: "other" for i, p in self.mind.master.players.items()},
                )
            )
        self.nearby_entities_walker[:] = widgets
        if widgets:
            closest_entity = self.nearby_entities_list[0]
            self.contents["body"] = (frames.ImageFrame(closest_entity.image), None)


class EquipmentFrame(SubMenuFrame):
    def __init__(self, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        super().__init__(mind, box)

    def on_update(self, deltatime: float) -> None:
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


class HelpFrame(SubMenuFrame):
    def __init__(self, mind):
        self.mind = mind
        map_commands = [
            "Map commands\n\n",
            f"←→↑↓:move\n",
            f"shift+←→↑↓:dash\n",
            f"a:attack\n",
            f"q:pickup\n",
        ]
        class_action_keys = [k for k in KeyMap]
        # for i, act in enumerate(self.player.class_actions):
        #     k = class_action_keys[i]
        #     map_commands.append(f"{k}:{self.player.class_actions[act].description.lower()}\n")
        menu_commands = [
            "Menu commands\n\n",
            f"tab:open/close\n",
            f"0/9-=:select item\n",
            f"ctrl+p:respawn\n",
            f"ctrl+a:inventory\n",
            f"ctrl+s:status\n",
            f"ctrl+d:help\n",
            f"ctrl+e:equipment\n",
        ]
        columns = urwid.Columns(
            [
                urwid.Text(map_commands, wrap="clip"),
                urwid.Text(menu_commands, wrap="clip"),
            ],
            dividechars=1,
        )
        super().__init__(mind, urwid.ListBox(urwid.SimpleListWalker([columns])))


CHARACTERS_SELECTION_FRAMES = {
    GenderType.FEMALE: {
        "selected": {k: None for k in CharacterSelectionFrame.options},
        "unselected": {k: None for k in CharacterSelectionFrame.options},
    },
    GenderType.MALE: {
        "selected": {k: None for k in CharacterSelectionFrame.options},
        "unselected": {k: None for k in CharacterSelectionFrame.options},
    },
}

for c in CharacterSelectionFrame.options:
    for gender in GenderType:
        for bkg in ("unselected", "selected"):
            if bkg == "selected":
                bkg_surface = ImageCollection.BACKGROUND_SELECTED.surface.copy()
            else:
                bkg_surface = ImageCollection.BACKGROUND_UNSELECTED.surface.copy()
            char_img = ImageCollection.CHARACTERS[gender][c].surface
            x_offset = (bkg_surface.get_width() - char_img.get_width()) // 2
            y_offset = bkg_surface.get_height() - char_img.get_height()
            bkg_surface.blit(char_img, (x_offset, y_offset))
            CHARACTERS_SELECTION_FRAMES[gender][bkg][c] = frames.ImageFrame(Image(bkg_surface))
