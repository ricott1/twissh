# encoding: utf-8

import urwid
import time, os, copy
from collections import OrderedDict
from rpg_game.utils import log, mod, distance
from rpg_game.constants import *
from urwid import raw_display


SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()
HEADER_HEIGHT = lambda : max(4, min(12, SIZE()[1]//12))
print(SIZE(), HEADER_HEIGHT())
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
            ("disabled","black","light gray"),
            ("red","dark red","black"),
            ("green","light green","black"),
            ("yellow","yellow","black"),
            ("white_line","black","white", "standout"),
            ("red_line","dark red","white", "standout"),
            ("green_line","light green","white", "standout"),
            ("yellow_line","yellow","white", "standout"),
            ("cyan","light cyan","black"),
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
        line = [urwid.Text("Choose your class")]            
        btn = create_button("Warrior", self.select_class, user_args=["Warrior"])
        line.append(btn)
        btn = create_button("Dwarf", self.select_class, user_args=["Dwarf"])
        line.append(btn)
        btn = create_button("Novice", self.select_class, user_args=["Novice"])
        line.append(btn)
        btn = create_button("Thief", self.select_class, user_args=["Thief"])
        line.append(btn)
        btn = create_button("Bard", self.select_class, user_args=["Bard"])
        line.append(btn)
        listbox = SelectableListBox(urwid.SimpleListWalker(line))
        self.listbox = listbox.body
        head = urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.Padding(
                urwid.BigText(('banner', "Hack\'n\'SSH"), urwid.HalfBlock5x4Font()),
                width='clip')
        ]))
        super().__init__(parent, mind, listbox)

    def select_class(self, _class, button):
        self.mind.master.new_player(self.mind.avatar.uuid, _class)
        self.parent.start_game_frame()
        

class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        header = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        _frames = ("Status", "Inventory", "Help")
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in _frames}
        idx = 2
        _title = _frames[idx]

        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        _footer = FrameColumns(self, screen_btns, dividechars=1)
        _footer.focus_position = idx
        _header = urwid.LineBox(urwid.BoxAdapter(header, HEADER_HEIGHT()))
        
        self.active_body = self.bodies[_title]
        self.map = MapFrame(self, mind)
        self.menu = UiFrame(parent, mind, self.bodies[_title], footer=_footer, focus_part="body")
        self._menu_view = True
        print("STARTING GUI", self.active_body)
        super().__init__(parent, mind, urwid.LineBox(self.menu, title=_title), header=_header, focus_part="body")

        self.header_widget = self.header.original_widget.box_widget

    @property
    def menu_view(self):
        return self._menu_view
    @menu_view.setter
    def menu_view(self, value):
        self._menu_view = value
        if self.menu_view:
            self.contents["body"] = (urwid.LineBox(self.menu, title=self.active_body), None)
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
        elif self.menu_view:
            if _input == "shift right":
                # self.menu.focus_position = "footer"
                self.menu.footer.focus_next() 
            elif _input == "shift left":
                # self.menu.focus_position = "footer"
                self.menu.footer.focus_previous() 
            elif _input == "s":
                self.menu.contents["body"] = (self.bodies["Status"], None)
                self.contents["body"] = (urwid.LineBox(self.menu, title="Status"), None)
            elif _input == "i":
                self.menu.contents["body"] = (self.bodies["Inventory"], None)
                self.contents["body"] = (urwid.LineBox(self.menu, title="Inventory"), None)
            elif _input == "h":
                self.menu.contents["body"] = (self.bodies["Help"], None)
                self.contents["body"] = (urwid.LineBox(self.menu, title="Help"), None)
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
        super().__init__(parent, mind, map_box)
        
    def on_update(self):
        _map = copy.deepcopy(self.player.location.map)
        x, y, z = self.player.position
        widget_height = SIZE()[1] - HEADER_HEIGHT() - FOOTER_HEIGHT - 2
        visible_map = [line for j, line in enumerate(_map) if abs(x-j)<widget_height//2]
        map_with_attr = [urwid.AttrMap(urwid.AttrMap(urwid.Text(line, wrap="clip"), {self.player.id:"player"}), {p.id:"other" for i, p in self.mind.master.players.items()}) for line in visible_map]
        self.map_box[:] = map_with_attr

    def handle_input(self, _input):
        self.player.handle_input(_input)

class InventoryFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.mind = mind
        drop = urwid.Text(("disabled", " Drop "))
        use = urwid.Text(("disabled", " Use "))
        self.unselected_item_action = SelectableColumns([(6, drop), (5, use)], dividechars=0)
        self.item_action = self.unselected_item_action
        self.inventory_box = SelectableListBox(urwid.SimpleListWalker(self.item_action))
        self.equipment_box = self.build_equipment_box()
        super().__init__(parent, mind, SelectableColumns([(20, self.inventory_box), (45, self.equipment_box)]))
        self.selection = None
        
    def build_equipment_box(self):
        def equip_item(typ, button):
            if self.selection:
                i = self.player.inventory.entities[self.selection]
                if i.is_equipment and not i.is_equipped:
                    self.player.equip(i, typ)
                self.selection = None
            else:
                self.player.unequip(typ)
                
            if self.player.equipment[typ]:
                eqp = self.player.equipment[typ]
                button.set_label((f"{eqp.color}", eqp.name))
            else:
                name = " ".join(typ.split("_"))
                name = name[0].upper() + name[1:]
                button.set_label(("white", name))

        _eqp_size = 45
        _btn_size = 13
        _side_size = 15
        _equipment = []

        _line = [(_side_size, urwid.Text(" "*_side_size)), 
                (_btn_size, create_button("Helm", equip_item, user_args=["helm"])), 
                (_side_size, urwid.Text(" "*_side_size))]
        column = SelectableColumns(_line, dividechars=0, _min=1, _max=self.player.inventory.horizontal_size)
        _equipment.append(column)

        _line = [(_btn_size, create_button("Main hand", equip_item, user_args=["main_hand"])),
                (_btn_size, create_button("Body", equip_item, user_args=["body"])),
                (_btn_size, create_button("Off hand", equip_item, user_args=["off_hand"]))]
        column = SelectableColumns(_line, dividechars=2, _min=1, _max=self.player.inventory.horizontal_size)
        _equipment.append(column)

        _line = [(_btn_size, create_button("Ring", equip_item, user_args=["ring"])),
                (_btn_size, create_button("Belt", equip_item, user_args=["belt"])), 
                (_btn_size, create_button("Gloves", equip_item, user_args=["gloves"]))]
        column = SelectableColumns(_line, dividechars=2, _min=1, _max=self.player.inventory.horizontal_size)
        _equipment.append(column)

        _line = [(_side_size, urwid.Text(" "*_side_size)), 
                (_btn_size, create_button("Boots", equip_item, user_args=["boots"])), 
                (_side_size, urwid.Text(" "*_side_size))]
        column = SelectableColumns(_line, dividechars=0, _min=1, _max=self.player.inventory.horizontal_size)
        _equipment.append(column)

        return SelectableListBox(urwid.SimpleListWalker(_equipment))
        
    def on_update(self):
        
        def select_item(item, button):
            if item:
                self.selection = item.id
                drop = create_button("Drop", drop_item, user_args = [item], borders=False)
                if item.is_consumable:
                    use = create_button("Use", consume_item, user_args = [item], borders=False)  
                else:
                    use = urwid.Text(("disabled", " Use "))
                self.item_action = SelectableColumns([(6, drop), (5, use)], dividechars=0) 
                
            else:
                self.selection = None
                self.item_action = self.unselected_item_action
                

        def drop_item(item, button):
            self.player.actions["drop"].use(self.player, obj=item)

        def consume_item(item, button):
            self.player.actions["consume"].use(self.player, obj=item)

        side = urwid.Text("║")

        _inventory = [urwid.Text("╔" +"═"*self.player.inventory.horizontal_size+"╗")]
        for x, line in enumerate(self.player.inventory.map):
            _line = [(1, side)]
            for y, l in enumerate(line):
                i = self.player.inventory.get((x, y, 0))
                if i and isinstance(l, tuple):
                    color, mark = l
                    if self.selection==i.id:
                        color = color + "_line"
                else:
                    mark = l
                    color = "white"

                _line.append((1, create_button(mark, select_item, user_args=[i],attr=color, focus_map = "line", borders=False)))
            _line += [(1, side)]  
            # column = SelectableColumns([(1, side)] + [(1, create_button(l, show_item, user_args=[l], borders=False)) for l in line]+[(1, side)], dividechars=0, _min=1, _max=self.player.inventory.horizontal_size)
            column = SelectableColumns(_line, dividechars=0, _min=1, _max=self.player.inventory.horizontal_size)
            try:
                index = self.inventory_box.focus_position
                column.focus_position = self.inventory_box.body[:][index].focus_position
            except:
                pass
            finally:
                _inventory.append(column)

        _inventory.append(urwid.Text("╚" +"═"*self.player.inventory.horizontal_size+"╝"))
        
        self.inventory_box.body[:] = _inventory + [self.item_action]

    def handle_input(self, _input):
        self.player.handle_input(_input)

class ListInventoryFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.inventory = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        super(InventoryFrame, self).__init__(parent, mind, self.inventory)
        self.selection = "normal"

    def on_update(self):
        def show_item(item, button):
            self.selection = item.id
        
        def back(button):
            self.selection = "normal"
            
        def drop_item(item, button):
            self.player.actions["drop"].use(self.player, obj=item)

        def consume_item(item, button):
            self.player.actions["consume"].use(self.player, obj=item)
            
        # def send_equip(item, button):
        #     if not item.is_equipped:
        #         self.player.equip(item)
            
        # def send_unequip(item, button):
        #     if item.is_equipped:
        #         self.player.unequip(item)

        
        widgets = []
        items = [i for i in self.player.inventory.all]
        if self.selection == "normal":
            for i in items:   
                line = []            
                btn = create_button(i.name, show_item, attr=i.color, user_args = [i])
                line.append((16, btn))
                
                
                # if i.is_equipment:
                #     if i.requisites(self.player):
                #         if i.is_equipped:
                #             bequip = urwid.Button("Unequip") 
                #             bequip._label.align = 'center'
                #             urwid.connect_signal(bequip, "click", send_unequip, user_args = [i])
                #         elif not i.is_equipped:
                #             bequip = urwid.Button("Equip") 
                #             bequip._label.align = 'center'
                #             urwid.connect_signal(bequip, "click", send_equip, user_args = [i])
                #     else:
                #         bequip = urwid.Button("Not Equipable") 
                #         bequip._label.align = 'center'                
                   
                bdrop = create_button("Drop", drop_item, user_args = [i])
                line.append((8, bdrop))
                if i.is_consumable:
                    btn = create_button("Use", consume_item, user_args = [i])  
                    line.append((8, btn))

                if i.is_equipment:
                    description = urwid.Text(f"- {i.eq_description}")
                else:
                    description = urwid.Text(f"- {i.description}")#, wrap="clip"
                line.append(description)
                
                columns = SelectableColumns(line, dividechars=2)
                try:
                    index = self.inventory.focus_position
                    columns.focus_position = self.inventory.body[:][index].focus_position
                except:
                    pass
                
                widgets.append(columns)
        else:
            i = next((it for it in items if it.id == self.selection), None)
            if i == None:
                self.selection = "normal"
            else:
                widgets.append(urwid.Text(i.status))
                if i.is_equipment:
                    description = urwid.Text((" - {} {}".format(i.eq_description, "(eq)"*int(i.is_equipped))))
                else:
                    description = urwid.Text(f"- {i.description}")
                widgets.append(description)
                
                bback = create_button("Back", back)
                
                widgets.append(SelectableColumns([(8, bback)]))       
        self.body.body[:] = widgets

class EquipmentFrame(UiFrame):    
    def __init__(self, parent, mind):
        super(EquipmentFrame, self).__init__(parent, mind, SelectableListBox(urwid.SimpleListWalker([urwid.Text("")])))
        self.selection = "normal"

    def on_update(self):
        def open_equipment(typ, button):
            self.selection = typ
            
        def send_equip(item, button):
            if not item.is_equipped:
                self.player.equip(item, self.selection)
            self.selection = "normal"
            
        def send_unequip(button):
            if self.selection in self.player.equipment and self.player.equipment[self.selection]:
                self.player.unequip(self.selection)
            self.selection = "normal"
             
        widgets = []
        
        if self.selection == "normal":
            t = urwid.Text("", align='center')
            widgets.append(t)
            
            for part, eqp in self.player.equipment.items():
                equip_btn = create_button(f"{' '.join(part.split('_'))}", open_equipment, user_args = [part])
                    
                if eqp:
                    text = urwid.Text([(eqp.color, f"{eqp.name} "), eqp.eq_description])
                else:
                    text = urwid.Text("None")
                line = [(16, equip_btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)    
                    
        else:
            t = urwid.Text(f"{' '.join(self.selection.split('_'))}", align='center')
            widgets.append(t)
            unequip_btn = create_button("None", send_unequip)
            text = urwid.Text("")
            line = [(16, unequip_btn), text]
            columns = SelectableColumns(line, dividechars=2)
            widgets.append(columns)
            eqs = [i for i in self.player.inventory.all if self.selection in i.type and i.requisites(self.player)]
            for i in eqs:
                btn = create_button(i.name, send_equip, attr=i.rarity, user_args = [i])
                text = urwid.Text(f"{'(eq)'*int(i.is_equipped)}")
                line = [(16, btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)

        self.body.body[:] = widgets

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
            min_dmg, max_dmg = weapon.dmg
        min_dmg = max(1, base + min_dmg)
        max_dmg = max(1, base + max_dmg)
        _right.append(f"╭──────────────────╮\n")
        _right.append(f"│ Attack {min_dmg:>3d}-{max_dmg:<3d}   │\n")
        _right.append(f"╰──────────────────╯\n")
        _right.append(f"╭──────────────────╮\n")
        _right.append(f"│ Dmg reduction {player.dmg_reduction:<2d} │\n")
        _right.append(f"╰──────────────────╯\n")
        

        self.box[:] = [urwid.Text(_top), urwid.Columns([urwid.Text(_left), urwid.Text(_right)], dividechars = 1) ]

class HelpFrame(UiFrame):    
    def __init__(self, parent, mind):
        self.mind = mind
        map_commands = ["Map commands\n\n", f"tab: open menu\n", f"←→↑↓: move\n", f"shift + ←→↑↓: dash\n", f"a: attack\n", f"q: pickup item\n"]
        for k, act in self.player.input_map.items():
            if act in self.player.class_actions:
                map_commands.append(f"{k}: {self.player.class_actions[act].description}\n")
        menu_commands = ["Menu commands\n\n", f"tab: close menu\n", f"←→↑↓: navigate menu\n", f"shift + ←→: change menu\n", f"enter: select\n", f"ctrl+p: respawn\n", f"s: status menu\n", f"i: inventory menu\n", f"h: help menu\n"]
        columns = urwid.Columns([urwid.Text(map_commands), urwid.Text(menu_commands)], dividechars = 4)
        super().__init__(parent, mind, urwid.ListBox(urwid.SimpleListWalker([columns])))


class ChatFrame(UiFrame):
    def __init__(self, parent, mind):
        
        self.footer = urwid.Edit("> ")

        self.output_walker = urwid.SimpleListWalker([])
        self.output_size = 0
        self.body = ExtendedListBox(
            self.output_walker)

        self.footer.set_wrap_mode("space")
        super(ChatFrame, self).__init__(parent, mind, self.body, 
                                 footer=self.footer)
        self.set_focus("footer")

    def on_update(self):
        for i in range(self.output_size, len(self.player.chat_received_log)):
            self.print_received_message(self.player.chat_received_log[i])
            self.output_size += 1

    def handle_input(self, _input):
        """ 
            Handle user inputs
        """

        # scroll the top panel
        if _input in ("page up","page down", "shift left", "shift right"):
            self.body.handle_input(_input)
        elif _input == "enter":
            # Parse data or (if parse failed)
            # send it to the current world
            text = self.footer.get_edit_text()

            self.footer.set_edit_text(" "*len(text))
            self.footer.set_edit_text("")

            if text.strip():
                self.print_sent_message(text)
                self.player.chat_sent_log.append({"sender_id":self.player.id, "sender":self.player.name, "time":time.time(), "text":text})

    def print_sent_message(self, text):
        self.output_walker.append(urwid.AttrMap(urwid.Text(f'You: {text}'), "uncommon"))
        self.body.scroll_to_bottom()
 
    def print_received_message(self, message):
        self.output_walker.append(urwid.Text(f"{message['sender']}: {message['text']}"))
        self.body.scroll_to_bottom()
                         
class SelectableListBox(urwid.ListBox):
    def __init__(self, body):
        super(SelectableListBox, self).__init__(body)

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
             

class SelectableColumns(urwid.Columns):
    def __init__(self, widget_list, dividechars=0, _min=None, _max=None):
        super(SelectableColumns, self).__init__(widget_list, dividechars)

    def focus_next(self):
        try: 
            self.focus_position += 1 
            if _max and self.focus_position > _max:
                self.focus_position = _max
        except:
            pass
    def focus_previous(self):
        try: 
            self.focus_position -= 1
            if _min and self.focus_position < _min:
                self.focus_position = _min
        except:
            pass

class FrameColumns(urwid.Columns):
    def __init__(self, parent, widget_list, dividechars=0):
        super(FrameColumns, self).__init__(widget_list, dividechars)
        self.parent = parent

    def focus_next(self):
        try: 
            self.focus_position += 1 
            new_body = [b for b in self.parent.bodies][self.focus_position]
            self.parent.update_body(new_body)
        except:
            pass
    def focus_previous(self):
        try: 
            self.focus_position -= 1
            new_body = [b for b in self.parent.bodies][self.focus_position]
            self.parent.update_body(new_body)
        except:
            pass

class ExtendedListBox(urwid.ListBox):
    """
        Listbow widget with embeded autoscroll
    """

    __metaclass__ = urwid.MetaSignals
    signals = ["set_auto_scroll"]


    def set_auto_scroll(self, switch):
        if type(switch) != bool:
            return
        self._auto_scroll = switch
        urwid.emit_signal(self, "set_auto_scroll", switch)

    auto_scroll = property(lambda s: s._auto_scroll, set_auto_scroll)


    def __init__(self, body):
        urwid.ListBox.__init__(self, body)
        self.auto_scroll = True


    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, "modified", self._invalidate)

        self.body = body
        self._invalidate()

        urwid.connect_signal(body, "modified", self._invalidate)


    def handle_input(self, _input):
        if _input == "shift left":
            _input = "page up"
        elif _input == "shift right":
            _input = "page down"
        urwid.ListBox.keypress(self, (80, 24), _input)

        if _input in ("page up", "page down"):
            if self.get_focus()[1] == len(self.body)-1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False

    def scroll_to_bottom(self):
        if self.auto_scroll:
            # at bottom -> scroll down
            self.set_focus(len(self.body)-1)

class ButtonLabel(urwid.SelectableIcon):
    def set_text(self, label):
        '''
        set_text is invoked by Button.set_label
        '''
        self.__super.set_text(label)
        self._cursor_position = len(label) + 1


class NoCursorButton(urwid.Button):
    '''
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged
    '''
    button_left = "["
    button_right = "]"

    def __init__(self, label, on_press=None, user_data=None, borders=True):
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

        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)

def create_button(label, cmd, attr=None, focus_map = "line", align = "center", user_args = None, borders=True):
    btn = NoCursorButton(label, borders=borders)
    btn._label.align = align
    if user_args:
        urwid.connect_signal(btn, "click", cmd, user_args = user_args)
    else:
        urwid.connect_signal(btn, "click", cmd)
    if attr or focus_map:
        return urwid.AttrMap(btn, attr, focus_map=focus_map)
    return btn
