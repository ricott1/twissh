# encoding: utf-8

import urwid
import time, os, copy
from rpg_game.utils import log, mod, distance
from rpg_game.constants import *
from urwid import raw_display


SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()


MIN_HEADER_HEIGHT = 4

FOOTER_HEIGHT = 5

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
            ("uncommon","light blue","black"),
            ("uncommon_line","light blue","white","standout"),
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
        print("HANDLING", _input)
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
        header = SelectableListBox(urwid.SimpleFocusListWalker([urwid.Text("")]))
        _frames = ("Status", "Inventory", "Help")
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in _frames}
        idx = 2
        _title = _frames[idx]

        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        _footer = FrameColumns(self, screen_btns, dividechars=1)
        _footer.focus_position = idx
        self.header_height = max(MIN_HEADER_HEIGHT, mind.screen_size[1]//4)
        _header = urwid.LineBox(urwid.BoxAdapter(header, self.header_height))
        
        self.active_body = self.bodies[_title]
        self.map = MapFrame(self, mind)
        self.menu = UiFrame(parent, mind, self.bodies[_title], footer=_footer, focus_part="footer")
        self._menu_view = True
        super().__init__(parent, mind, urwid.LineBox(self.menu, title=_title), header=_header, focus_part="body")

        self.header_widget = self.header.original_widget.box_widget

    @property
    def menu_view(self):
        return self._menu_view
    @menu_view.setter
    def menu_view(self, value):
        self._menu_view = value
        if self.menu_view:
            _title = next((t for t in self.bodies if self.active_body is self.bodies[t]), "")
            self.contents["body"] = (urwid.LineBox(self.menu, title=_title), None)
        else:
            self.contents["body"] = (self.map, None)

    @property
    def header_list(self):
        return sorted([ent for k, ent in self.player.location.entities.items() if distance(self.player.position, ent.position) <= 3 and ent.status], key=lambda ent: distance(self.player.position, ent.position))

    def update_body(self, _title):
        if self.menu_view:
            self.active_body = self.bodies[_title]
            self.menu.contents["body"] = (self.active_body, None)
            self.contents["body"] = (urwid.LineBox(self.menu, title=_title), None)

    def on_update(self):
        self.update_header()
        
        if self.menu_view:
            self.active_body.on_update()    
        else:
            self.map.on_update() 
    
    def handle_input(self, _input):
        if _input == "tab":
            self.menu_view = not self.menu_view
            if self.menu_view:
                self.menu.focus_position = "footer"
        elif self.menu_view:
            if _input == "d":
                self.menu.focus_position = "footer"
                self.menu.footer.focus_next() 
            elif _input == "a":
                self.menu.focus_position = "footer"
                self.menu.footer.focus_previous() 
            elif _input == "s":
                self.menu.focus_position = "footer"
                self.menu.footer.focus_position = 0
                self.update_body("Status")
            elif _input == "i":
                self.menu.focus_position = "footer"
                self.menu.footer.focus_position = 1
                self.update_body("Inventory")
            elif _input == "h":
                self.menu.focus_position = "footer"
                self.menu.footer.focus_position = 2
                self.update_body("Help")
            else:
                self.menu.focus_position = "body"
        elif not self.menu_view:
            self.map.handle_input(_input)
       
    def update_header(self):
        widgets = []
        for p in self.header_list:
            text = urwid.Text(p.status)
            if p is self.player:
                widgets.append(urwid.AttrMap(text, None, {"top" : "line", "name": "green_line", "green": "green_line", "yellow": "yellow_line", "red": "red_line"}))
            else:
                widgets.append(urwid.AttrMap(text, None, {"top" : "line", "name": "line", "green": "green_line", "yellow": "yellow_line", "red": "red_line"}))
        if widgets:
            self.header_widget.body[:] = widgets


class MapFrame(UiFrame):    
    def __init__(self, parent, mind):
        map_box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.map_box = map_box.body
        self.layer_view = "full"
        self.debug_view = False
        super().__init__(parent, mind, map_box)

    @property
    def visible_range(self):
        header_height = self.parent.header_height + 2
        tot_rows = self.mind.screen_size[1]
        return (tot_rows - header_height)

        
    def on_update(self):
        if self.layer_view == "full":
            _map = copy.deepcopy(self.player.location.map)
        else:
            _map = self.player.location.layer_from_entities(self.layer_view, self.debug_view)
        x, y, z = self.player.position
        if x > self.visible_range//2:
            visible_map = [line for j, line in enumerate(_map) if abs(x-j)<self.visible_range//2]
        else:
            visible_map = [line for j, line in enumerate(_map) if j<self.visible_range]
        map_with_attr = [urwid.AttrMap(urwid.AttrMap(urwid.Text(line, wrap="clip"), {self.player.id:"player"}), {p.id:"other" for i, p in self.mind.master.players.items()}) for line in visible_map]
        self.map_box[:] = map_with_attr

    def handle_input(self, _input):
        if _input == "0":
            self.layer_view = 0
            self.debug_view = False
        elif _input == "1":
            self.layer_view = 1
            self.debug_view = False
        elif _input == "2":
            self.layer_view = 2
            self.debug_view = False
        if _input == "4":
            self.layer_view = 0
            self.debug_view = True
        elif _input == "5":
            self.layer_view = 1
            self.debug_view = True
        elif _input == "6":
            self.layer_view = 2
            self.debug_view = True
        else:
            self.layer_view = "full"
        self.player.handle_input(_input)


class InventoryFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.mind = mind
        self._selection = None
        self.last_selected_btn = None
        self._highlight = None

        self.drop_btn = create_button("Drop", borders=False, disabled=True)
        self.use_btn = create_button("Use", borders=False, disabled=True)
        urwid.connect_signal(self.drop_btn, "click", self.drop_item)
        urwid.connect_signal(self.use_btn, "click", self.consume_item)
        _item_btn_size = (self.player.inventory.horizontal_size//2) +1
        self.item_action = SelectableColumns([(_item_btn_size, urwid.AttrMap(self.drop_btn, "disabled")), (_item_btn_size, urwid.AttrMap(self.use_btn, "disabled"))], dividechars=0)
        
        self.eqp_btns = {k: self.eqp_button(k) for k in self.player.equipment}
        self.inventory_box = SelectableListBox(urwid.SimpleFocusListWalker(self.item_action))    

        self.equipment_box = SelectableListBox(urwid.SimpleFocusListWalker(self.data_columns))
        self.update_equipment_box()
        super().__init__(parent, mind, SelectableColumns([(20, self.inventory_box), (55, self.equipment_box)]))
        self.body.focus_position = 1
    
    @property
    def selection_data(self):
        if not self.selection:
            return urwid.Text("")
        item = self.player.inventory.entities[self.selection.id]
        _text = [(item.color, f"{item.name}\n"), f"{item.description}\n"]
        if item.is_equipment:
            _text += [item.eq_description]
            if not item.requisites(self.player):
                _text += [("red", "not equippable")]
        return urwid.Text(_text)
    @property
    def highlight_data(self):
        if not self.highlight:
            return urwid.Text("")
        item = self.highlight
        _text = [(item.color, f"{item.name}\n"), f"{item.description}\n"]
        if item.is_equipment:
            _text += [item.eq_description]
            if not item.requisites(self.player):
                _text += [("red", "not equippable")]
        return urwid.Text(_text)
    @property
    def data_columns(self):
        return urwid.Columns([(25, self.highlight_data), (25, self.selection_data)])

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value):
        #if reselect, deselect
        if self._highlight == value:
            return

        self._highlight = value
        _equipment = self.equipment_box.body[:]
        _equipment[-1] = self.data_columns
        self.equipment_box.body[:] = _equipment
    

    @property
    def selection(self):
        if self._selection and self._selection.id not in self.player.inventory.entities:
            self.selection = None
        return self._selection

    @selection.setter
    def selection(self, value):
        #if reselect, deselect
        if self._selection == value:
            self._selection = None
        else:
            self._selection = value
        if not self.selection:
            self.use_btn.disabled = True
            use = urwid.AttrMap(self.use_btn, "disabled")
            self.drop_btn.disabled = True
            drop = urwid.AttrMap(self.drop_btn, "disabled")
            self.last_selection_position = None
        else:
            self.drop_btn.disabled = False
            drop = urwid.AttrMap(self.drop_btn, None, "line")
            if self.selection.is_consumable:
                self.use_btn.disabled = False
                use = urwid.AttrMap(self.use_btn, None, "line")
            else:
                self.use_btn.disabled = True
                use = urwid.AttrMap(self.use_btn, "disabled")

        _item_btn_size = (self.player.inventory.horizontal_size//2) +1
        self.item_action = SelectableColumns([(_item_btn_size, drop), (_item_btn_size, use)], dividechars=0)
        self.eqp_btns = {k: self.eqp_button(k) for k in self.player.equipment}
        self.update_equipment_box()

    def update_description(self):
        print("item")

    def drop_item(self, button):
        self.player.actions["drop"].use(self.player, obj=self.selection)
        self.selection = None

    def consume_item(self, button):
        self.player.actions["consume"].use(self.player, obj=self.selection)
        self.selection = None

    def equip_item(self, typ, button):
        if self.selection and self.selection.is_equipment and typ in self.selection.type:
            self.player.equip(self.selection)
            self.selection = None
        elif not self.selection and self.player.equipment[typ]:
            for t in self.player.equipment[typ].type:
                self.player.unequip(t)
            #self.eqp_btns[typ] = self.eqp_button(typ) 
            self.selection = None
            
    def eqp_button(self, typ):
        name = " ".join(typ.split("_"))
        name = "No " + name[0].upper() + name[1:]
        btn = create_button(name, disabled=False)
        urwid.connect_signal(btn, "click", self.equip_item, user_args=[typ]) 
        if self.player.equipment[typ]:
            eqp = self.player.equipment[typ]
            btn.set_label(eqp.name)

        if self.selection and (not self.selection.is_equipment or typ not in self.selection.type):
            btn.disabled = True
            return urwid.AttrMap(btn, "disabled")
        
        if self.player.equipment[typ]:
            return urwid.AttrMap(btn, f"{eqp.color}", f"{eqp.color}_line")
        
        return urwid.AttrMap(btn, None, "line")

    def update_equipment_box(self):
        _eqp_size = 45
        _btn_size = 25
        _side_size = 15
        _equipment = []

        _line = [(_btn_size, self.eqp_btns["helm"]),
                (_btn_size, self.eqp_btns["body"])]
        column = SelectableColumns(_line, dividechars=0)
        _equipment.append(column)

        _line = [(_btn_size, self.eqp_btns["main_hand"]),
                (_btn_size, self.eqp_btns["off_hand"])]
        column = SelectableColumns(_line, dividechars=0)
        _equipment.append(column)

        _line = [(_btn_size, self.eqp_btns["ring"]), 
                (_btn_size, self.eqp_btns["gloves"])]
        column = SelectableColumns(_line, dividechars=0)
        _equipment.append(column)

        _line = [(_btn_size, self.eqp_btns["belt"]), 
                (_btn_size, self.eqp_btns["boots"])]
        column = SelectableColumns(_line, dividechars=0)
        _equipment.append(column)

        self.equipment_box.body[:] = _equipment + [self.data_columns]
        
    def update_inventory_box(self):
        
        def select_item(item, button):
            '''item can be None, for an empty square'''
            #move item to button position if item=None or item is self.selection
            if self.last_selected_btn is button:
                self.selection = None
                self.last_selected_btn = None
            elif self.selection and (not item or item is self.selection):
                bx, by = button.position
                lx, ly = self.last_selected_btn.position
                delta_x, delta_y = (bx-lx, by-ly)
                extra_pos = [(0,0,0)] + self.selection.in_inventory_extra_positions
                x, y, z = self.selection.position
                if all([self.selection.location.get((x+xp+delta_x, y+yp+delta_y, z+zp)) in (None, self.selection) and not self.selection.location.out_of_bounds((x+xp+delta_x, y+yp+delta_y, z+zp)) for xp, yp, zp in extra_pos]):
                    self.selection.position = (x+delta_x, y+delta_y, z)
                    self.selection = None
                    self.last_selected_btn = None
            else:
                self.selection = item
                self.last_selected_btn = button

        side = urwid.Text("║")
        _inventory = [urwid.Text("╔" +"═"*self.player.inventory.horizontal_size+"╗")]
        for x, line in enumerate(self.player.inventory.map):
            _line = [(1, side)]
            for y, l in enumerate(line):
                i = self.player.inventory.get((x, y, 0))
                if i and isinstance(l, tuple):
                    color, mark = l
                    if self.selection is i:
                        color = color + "_line"
                else:
                    mark = "."
                    color = "disabled"

                btn = create_button(mark, select_item, user_args=[i], borders=False)
                btn.position = (x, y)
                _line.append((1, urwid.AttrMap(btn, color, focus_map="line")))
            _line += [(1, side)]  
            column = SelectableColumns(_line, dividechars=0)

            try:
                index = self.inventory_box.focus_position
                column.focus_position = self.inventory_box.body[:][index].focus_position
                active_btn = self.inventory_box.body[:][index][column.focus_position]
                x, y = active_btn.position
                self.highlight = self.player.inventory.get((x, y, 0))
            except:
                pass
            finally:
                _inventory.append(column)

        _inventory.append(urwid.Text("╚" +"═"*self.player.inventory.horizontal_size+"╝"))
        
        self.inventory_box.body[:] = _inventory + [self.item_action]

    def on_update(self):
        self.update_inventory_box()
        #self.update_equipment_box()

class StatusFrame(UiFrame):    
    def __init__(self, parent, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        super().__init__(parent, mind, box)

    def on_update(self):
        # index = self.parent.header_widget.focus_position
        # player = self.header_list[index] #keep this in change we allow to change focus later on
        player = self.player
        _top = f" {player.name:<14s} {player.game_class.name:>12s} Lev:{player.level:<2d} Exp:{player.exp:<6d} {player.location.name}@{player.position}\n"

        _left = []
        _left.append(f"╭──────────────────────╮\n")

        for s in ["STR", "INT", "WIS", "CON", "DEX", "CHA"]:
            c = getattr(player, s)
            state = ["normal", "positive", "negative"][-int(c.bonus < 0) + int(c.bonus > 0)]
            _left += [f"│ {c.name:<12} ", (state, f"{c.value:>2d}"), f" ({c.mod:<+2d}) │\n"]
        
        _left.append(f"╰──────────────────────╯\n")
        
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
        _right.append(f"╭────────────────╮\n")
        _right.append(f"│ Damage {min_dmg:>3d}-{max_dmg:<3d} │\n")
        _right.append(f"│ Reduction {player.dmg_reduction:<3d}  │\n")
        _right.append(f"│ Encumbrance {player.encumbrance:<2d} │\n")
        _right.append(f"╰────────────────╯\n")
        

        self.box[:] = [urwid.Text(_top), urwid.Columns([urwid.Text(_left), urwid.Text(_right)], dividechars = 1) ]


class HelpFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.mind = mind
        map_commands = ["Map commands\n\n", f"tab: open menu\n", f"←→↑↓: move\n", f"shift + ←→↑↓: dash\n", f"a: attack\n", f"q: pickup item\n"]
        for k, act in self.player.input_map.items():
            if act in self.player.class_actions:
                map_commands.append(f"{k}: {self.player.class_actions[act].description.lower()}\n")
        menu_commands = ["Menu commands\n\n", f"tab: close menu\n", f"←→↑↓: navigate menu\n", f"a/d: change menu\n", f"enter: select\n", f"ctrl+p: respawn\n", f"s: status menu\n", f"i: inventory menu\n", f"h: help menu\n"]
        columns = urwid.Columns([urwid.Text(map_commands), urwid.Text(menu_commands)], dividechars = 4)
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

    
