# encoding: utf-8

import urwid
import time, os, copy
from rpg_game.utils import log, mod, distance
from rpg_game.constants import *
from urwid import raw_display


SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()


MIN_HEADER_HEIGHT = 3
MAX_MENU_WIDTH = 48
FOOTER_HEIGHT = 4

PALETTE = [
            ("line", 'black', 'white', "standout"),
            ("top","white","black"),
            ("frame","white","white"),
            ("player", "light green", "black"),
            ("other", "light blue", "black"),
            ("monster", "dark red", "black"),
            ("fatigued", "dark red", "white", "standout"),
            ("reversed", "standout", ""),

            ("common","white","black"),
            ("common_line","black","white","standout"),
            ("uncommon","dark cyan","black"),
            ("uncommon_line","dark cyan","white","standout"),
            ("rare","yellow","black"),
            ("rare_line","yellow","white","standout"),
            ("unique","light magenta","black"),
            ("unique_line","light magenta","white","standout"),
            ("set","light green","black"),
            ("set_line","light green","white","standout"),

            ("normal","white","black"),
            ("positive","light green","black"),
            ("negative","dark red","black"),
            ("white","white","black"),
            ("disabled","dark red","black"),
            ("red","dark red","black"),
            ("green","light green","black"),
            ("yellow","yellow","black"),
            ("brown","brown","black"),
            ("white_line","black","white", "standout"),
            ("red_line","dark red","white", "standout"),
            ("green_line","light green","white", "standout"),
            ("yellow_line","yellow","white", "standout"),
            ("cyan","light cyan","black"),
            ("cyan_line","light cyan","white", "standout"),
            ("name","white","black"),
            ]


class UiFrame(urwid.Frame):
    def __init__(self, parent, mind, *args, **kargs):
        self.parent = parent 
        self.mind = mind
        urwid.AttrMap(self,"frame")
        super().__init__(*args, **kargs)

    @property
    def player(self):
        if self.mind.avatar.uuid in self.mind.master.players:
            return self.mind.master.players[self.mind.avatar.uuid]
        else: 
            return None

    @property
    def connection(self):
        if self.mind.avatar.uuid in self.mind.connections:
            return self.mind.connections[self.mind.avatar.uuid]
        else: 
            return None

    def handle_input(self, _input):
        pass

    def on_update(self):
        pass

    def dispatch_event(self, event_type, *args):
        self.mind.get_GUI_event(event_type, *args)

    def register_event(self, event_type, callback):
        self.mind.register_GUI_event(event_type, callback)

    def disconnect(self):
        pass

    def restart(self):
        pass

    def focus_next(self):
        pass

    def focus_previous(self):
        pass

    def update_body(self, title, no_title=False, boxed=False):
        self.active_body = self.bodies[title]
        if boxed:
            if no_title:
                self.contents["body"] = (urwid.LineBox(self.active_body), None)
            else:
                self.contents["body"] = (urwid.LineBox(self.active_body, title=title), None)
        else:
            self.contents["body"] = (self.active_body, None)

class GUI(UiFrame):
    def __init__(self, parent, mind):
        self.bodies = {"Intro" : IntroFrame(self, mind)}
        self.active_body = self.bodies["Intro"]
        super().__init__(parent, mind, self.active_body)

    def on_update(self):
        self.active_body.on_update()
    
    def handle_input(self, _input):
        # print("HANDLING", _input)
        self.active_body.handle_input(_input)
    
    # def exit(self):
    #     self.disconnect()
    #     self.mind.disconnect()#should use dispatch event

    def restart(self):
        self.update_body("Intro", no_title=True)

    def start_game_frame(self):
        self.bodies["Game"] = GameFrame(self, self.mind)
        self.update_body("Game", no_title=True)
  
class IntroFrame(UiFrame):
    def __init__(self, parent, mind):
        # urwid.Padding(urwid.BigText(('top', "Hack\'n\'SSH"), urwid.HalfBlock5x4Font())),
        self.choices = ("Warrior", "Dwarf", "Wizard", "Thief", "Bard")
        self.descriptions = {"Warrior": "The mighty warrior\n\nStrength +1, Hit points +4\nCharge and parry", 
                             "Dwarf": "The short dwarf\n\nStrength +1, Constitution +1, Hit points +6\nDemolish and parry",
                             "Wizard": "The opportune wizard\n\nIntelligence +1\n Fireball, teleport and ice wall",
                             "Thief": "The sneaky thief\n\nDexterity +1, Intelligence +1, Hit points +2\nSneak attack, hide and trap",
                             "Bard": "The noisy bard\n\nCharisma +1, Dexterity +1, Intelligence +1, Hit points +2\nSing and summon"}
        line = []
        for c in self.choices:            
            btn = attr_button(c, self.select_class)
            line.append(btn)
        walker = urwid.SimpleFocusListWalker(line)
        urwid.connect_signal(walker, "modified", self.update_description)
        self.listbox = SelectableListBox(walker)
        header = urwid.LineBox(urwid.BoxAdapter(self.listbox, len(self.choices)+1))

        super().__init__(parent, mind, urwid.ListBox(urwid.SimpleListWalker([urwid.Text(self.descriptions["Warrior"])])), header=header, focus_part="header")

    def select_class(self, button):
        index = min(self.listbox.focus_position, len(self.choices)-1)
        choice = self.choices[index]
        self.mind.master.new_player(self.mind.avatar.uuid, choice)
        self.parent.start_game_frame()

    def update_description(self):
        index = min(self.listbox.focus_position, len(self.choices)-1)
        choice = self.choices[index]
        self.contents["body"] = (urwid.ListBox(urwid.SimpleListWalker([urwid.Text(self.descriptions[choice])])), None)
        

class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        self.mind = mind

        _header = urwid.LineBox(urwid.BoxAdapter(SelectableListBox(urwid.SimpleFocusListWalker([urwid.Text("")])), self.header_height))
        
        self._menu_view = True
        self.map = MapFrame(self, mind)
        self.menu = MenuFrame(self, mind)
        
        super().__init__(parent, mind, urwid.Columns([(self.map_width, self.map), (self.menu_width, self.menu)], focus_column=1), header=_header, footer=None, focus_part="body")
        
        self.menu_view = True
        self.update_footer()
        self.header_widget = self.header.original_widget.box_widget
        self.footer_content_size = 0

    @property
    def header_height(self):
        return MIN_HEADER_HEIGHT#max(MIN_HEADER_HEIGHT, self.mind.screen_size[1]//8)
    
    @property
    def menu_width(self):
        if self.menu_view:
            return min(MAX_MENU_WIDTH, (3*self.mind.screen_size[0])//7)
        return 0

    @property
    def map_width(self):
        if self.menu_view:
            return self.mind.screen_size[0] - self.menu_width
        return self.mind.screen_size[0]

    @property
    def body_width(self):
        return self.mind.screen_size[0]

    @property
    def body_height(self):
        return self.mind.screen_size[1] - self.header_height - FOOTER_HEIGHT - 2

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
        return sorted([ent for k, ent in self.player.location.entities.items() if distance(self.player.position, ent.position) <= 3 and ent.status], key=lambda ent: distance(self.player.position, ent.position))

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

    def on_update(self):
        self.update_header()
        if self.footer_content_size != len(self.player.inventory.all):
            self.update_footer()
        if self.mind.screen_size != (80, 24):
            self.update_footer()
        self.map.on_update() 
        if self.menu_view:
            self.menu.on_update()
    
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
        elif _input == self.mind.key_map["status-menu"] and self.menu_view:
                self.menu.update_body("Status")
        elif _input == self.mind.key_map["help-menu"] and self.menu_view:
                self.menu.update_body("Help")
        elif _input == self.mind.key_map["equipment-menu"] and self.menu_view:
                self.menu.update_body("Equipment")
        elif _input == self.mind.key_map["inventory-menu"] and self.menu_view:
                self.menu.update_body("Inventory")
        else:
            self.map.handle_input(_input)

    def select_item(self, _input):
        if _input.isnumeric() and int(_input) > 0:
            _input = int(_input)-1
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
            widgets.append(urwid.AttrMap(urwid.AttrMap(urwid.Text(p.status, wrap="clip"), {self.player.id:"player"}), {p.id:"other" for i, p in self.mind.master.players.items()}))
        if widgets:
            self.header_widget.body[:] = widgets



class MapFrame(UiFrame):    
    def __init__(self, parent, mind):
        map_box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.map_box = map_box.body
        self.layer_view = -1
        self.debug_view = False
        super().__init__(parent, mind, map_box)
        self.on_update()

    @property
    def visible_range(self):
        header_height = self.parent.header_height + 2
        tot_rows = self.mind.screen_size[1]
        return (tot_rows - header_height - FOOTER_HEIGHT)

        
    def on_update(self):
        if self.layer_view == -1:
            _map = copy.deepcopy(self.player.location.map)
        else:
            _map = self.player.location.layer_from_entities(self.layer_view, self.debug_view)

        x, y, z = self.player.position
        w = max(0, y - self.parent.body_width//3)
        visible_map = [line[w:w+self.parent.body_width] for line in _map]
        h = max(0, x - self.parent.body_height//2)
        if h+self.parent.body_height >= len(visible_map):
            visible_map = visible_map[len(visible_map)-self.parent.body_height:]
        else:
            visible_map = visible_map[h:h+self.parent.body_height]

        map_with_attr = [urwid.AttrMap(urwid.AttrMap(urwid.Text(line, wrap="clip"), {self.player.id:"player"}), {p.id:"other" for i, p in self.mind.master.players.items()}) for line in visible_map]
        self.map_box[:] = map_with_attr

    def handle_input(self, _input):
        if _input == "ctrl f":
            self.debug_view = not self.debug_view
        elif _input == "ctrl v":
            self.layer_view = self.layer_view + 1
            if self.layer_view > 2:
                self.layer_view = -1 
        elif _input in self.mind.key_map:
            _action = self.mind.key_map[_input]
            self.player.handle_input(_action)

class MenuFrame(UiFrame):
    def __init__(self, parent, mind):
        _frames = ("Inventory", "Status", "Equipment", "Help")
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in _frames}
        idx = -1
        _title = _frames[idx]
        self.active_body = self.bodies[_title]
        super().__init__(parent, mind, urwid.LineBox(self.active_body, title=_title))

    def on_update(self):
        self.active_body.on_update()

    def selectable(self):
        return False

    def update_body(self, _title):
        self.active_body = self.bodies[_title]
        self.contents["body"] = (urwid.LineBox(self.active_body, title=_title), None)

class InventoryFrame(UiFrame):    
    def __init__(self, parent, mind):
        columns = urwid.Columns([urwid.Text("")]) 
        box = urwid.ListBox(urwid.SimpleListWalker([columns]))
        self.box = box.body
        self.default_header = urwid.Text("0/9-= to select\n\n", align="center")
        self.default_footer = urwid.Text([("green", f"{'Enter:use/eqp':<14s}"), ("yellow", "Q:drop")], align="center")
        super().__init__(parent, mind, box, header=self.default_header, footer=self.default_footer)
    
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
            self.contents["header"] = (urwid.Text([(i.color, f"{i.name}\n"), f"{i.description}\n"], align="center"), None)

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
        
        _marker_box = ["╔" +"═"*width+"╗\n"]
        for x in range(height):
            _marker_box += ["║"]
            for y in range(width):
                _marker_box += ["."] 
            _marker_box += ["║\n"]
        _marker_box += ["╚" +"═"*width+"╝"]
        if self.player.inventory.selection:
            i = self.player.inventory.selection
            X_OFFSET = 2
            Y_OFFSET = 4
            for m, pos in zip(i.in_inventory_markers, i.in_inventory_marker_positions):
                x, y = pos
                _marker_box[(x+X_OFFSET)*(width+2)+y+Y_OFFSET] = (i.color, m)
        self.box[:] = [urwid.Columns([(width+2, urwid.Text(_marker_box)), self.selection_data], dividechars=1)]

    def on_update(self):
        self.update_header()
        self.update_body()
        self.update_footer()


class StatusFrame(UiFrame):    
    def __init__(self, parent, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        super().__init__(parent, mind, box)

    def on_update(self):
        player = self.player
        x, y, z = player.position
        _top = f"{player.name:<12s} {player.game_class.name:<10s}\nLev:{player.level:<2d} Exp:{player.exp:<4d} {player.location.name}@({x},{y})\n"

        _left = []

        for s in CHARACTERISTICS:
            c = getattr(player, s)
            state = ["normal", "positive", "negative"][-int(c.temp_bonus < 0) + int(c.temp_bonus > 0)]
            if self.parent.parent.menu_width > 40:
                _name = c.name[0].upper() + c.name[1:]
                _left += [f"{_name:<12} ", (state, f"{c.value:>2d}"), f" ({c.mod:<+2d})\n"]
            elif self.parent.parent.menu_width > 36:
                _name = c.name[0].upper() + c.name[1:6]
                _left += [f"{_name:<6} ", (state, f"{c.value:>2d}"), f" ({c.mod:<+2d})\n"]
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
        if player.inventory.encumbrance == EXTRA_ENCUMBRANCE_MULTI*player.encumbrance:
            _right.append(("red", f"{player.inventory.encumbrance:>2d}"))
        elif player.inventory.encumbrance > player.encumbrance:
            _right.append(("yellow", f"{player.inventory.encumbrance:>2d}"))
        else:
            _right.append(("white", f"{player.inventory.encumbrance:>2d}"))
        _right.append(f"/{player.encumbrance:<2d}\n")
        _right.append(f"Speed {player.movement_speed}\n")
        _right.append(f"Monsterized {player.MP:<2d}\n")
        
        self.box[:] = [urwid.Text(_top), urwid.Columns([urwid.Text(_left), urwid.Text(_right)], dividechars = 1) ]


class EquipmentFrame(UiFrame):    
    def __init__(self, parent, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        super().__init__(parent, mind, box)

    def on_update(self):
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


class HelpFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.mind = mind
        map_commands = ["Map commands\n\n",  f"←→↑↓:move\n", f"shift+←→↑↓:dash\n", f"a:attack\n", f"q:pickup\n"]
        class_action_keys = [k for k, act in self.mind.key_map.items() if act.startswith("class_ability")]
        for i, act in enumerate(self.player.class_actions):
            k = class_action_keys[i]
            map_commands.append(f"{k}:{self.player.class_actions[act].description.lower()}\n")
        menu_commands = ["Menu commands\n\n", f"tab:open/close\n",f"0/9-=:select item\n", f"ctrl+p:respawn\n", f"ctrl+a:inventory\n", f"ctrl+s:status\n", f"ctrl+d:help\n", f"ctrl+e:equipment\n"]
        columns = urwid.Columns([urwid.Text(map_commands, wrap="clip"), urwid.Text(menu_commands, wrap="clip")], dividechars = 1)
        super().__init__(parent, mind, urwid.ListBox(urwid.SimpleListWalker([columns])))

                    
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
    def __init__(self, widget_list, focus_column=None, dividechars=0):
        super().__init__(widget_list, dividechars, focus_column)

    def focus_next(self):
        try: 
            self.focus_position += 1
        except:
            pass
    def focus_previous(self):
        try: 
            self.focus_position -= 1
        except:
            pass

class FrameColumns(urwid.Columns):
    def __init__(self, parent, widget_list, dividechars=0):
        self.widget_size = len(widget_list)
        super(FrameColumns, self).__init__(widget_list, dividechars)
        self.parent = parent

    def focus_next(self):
        try: 
            self.focus_position += 1
            if self.focus_position >= self.widget_size:
                self.focus_position -= self.widget_size
            new_body = [b for b in self.parent.bodies][self.focus_position]
            self.parent.update_body(new_body)
        except:
            pass
    def focus_previous(self):
        try: 
            self.focus_position -= 1
            if self.focus_position < 0:
                self.focus_position += self.widget_size
            new_body = [b for b in self.parent.bodies][self.focus_position]
            self.parent.update_body(new_body)
        except:
            pass


class ButtonLabel(urwid.SelectableIcon):
    def set_text(self, label):
        '''
        set_text is invoked by Button.set_label
        '''
        self.__super.set_text(label)
        self._cursor_position = len(label) + 1


class MyButton(urwid.Button):
    '''
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged
    '''
    button_left = "["
    button_right = "]"

    def __init__(self, label, on_press=None, user_data=None, borders=True, disabled=False):
        self._label = ButtonLabel("")
        if borders:
            cols = urwid.Columns([
                ('fixed', len(self.button_left), urwid.Text(self.button_left)),
                self._label,
                ('fixed', len(self.button_right), urwid.Text(self.button_right))],
                dividechars=1)
        else:
            cols = urwid.Columns([self._label],
                dividechars=0)

        super(urwid.Button, self).__init__(cols)

        self.disabled = disabled
        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)
        self.lllavel = label

    # @property
    # def disabled(self):
    #     return self._disabled
    # @disabled.setter
    # def disabled(self, value):
    #     if self._disabled == value:
    #         return
    #     if self.disabled:
    #         urwid.AttrMap(self, "disabled")
    #     else:
    #         urwid.AttrMap(self, None, "line")

    def selectable(self):
        return not self.disabled

def attr_button(label, cmd=None, attr_map=None, focus_map = "line", align = "center", user_args = None, borders=True, disabled=False):
    btn = create_button(label, cmd=cmd, align = align, user_args = user_args, borders=borders, disabled=disabled)
    return urwid.AttrMap(btn, attr_map, focus_map=focus_map)


def create_button(label, cmd=None, align = "center", user_args = None, borders=True, disabled=False):
    btn = MyButton(label, borders=borders, disabled=disabled)
    btn._label.align = align
    if cmd:
        if user_args:
            urwid.connect_signal(btn, "click", cmd, user_args = user_args)
        else:
            urwid.connect_signal(btn, "click", cmd)
    return btn

    
