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
            ("uncommon","light blue","black"),
            ("rare","yellow","black"),
            ("unique","light magenta","black"),
            ("set","light green","black"),
            ("normal","white","black"),
            ("positive","light green","black"),
            ("negative","dark red","black"),
            ("white","white","black"),
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
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Intro", "Game")}
        #self.update_body("Intro", no_title=True)
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
  
class IntroFrame(UiFrame):
    def __init__(self, parent, mind):
        line = [urwid.Text("Choose your class")]            
        btn = create_button("Warrior", self.select_class, user_args=["Warrior"])
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
        self.parent.update_body("Game")


class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        header = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Status", "Inventory", "Equipment")}
        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        _footer = FrameColumns(self, screen_btns)
        _header = urwid.LineBox(urwid.BoxAdapter(header, HEADER_HEIGHT()))
        _title = "Status"
        self.active_body = _title
        self.map = MapFrame(self, mind)
        self.menu = UiFrame(parent, mind, self.bodies[self.active_body], footer=_footer, focus_part="footer")
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
            self.contents["body"] = (urwid.LineBox(self.menu, title=self.active_body), None)
        else:
            self.contents["body"] = (self.map, None)

    @property
    def header_list(self):
        return sorted([ent for k, ent in self.player.location.entities.items() if distance(self.player.position, ent.position) <= 3], key=lambda ent: distance(self.player.position, ent.position))

    def update_body(self, title):
        if self.menu_view:
            self.active_body = title
            self.menu.contents["body"] = (self.bodies[self.active_body], None)
            self.contents["body"] = (urwid.LineBox(self.menu, title=self.active_body), None)

    def on_update(self):
        self.update_header()
        
        if self.menu_view:
            self.bodies[self.active_body].on_update()    
        else:
            self.map.on_update() 
    
    def handle_input(self, _input):
        if _input == "tab":
            self.menu_view = not self.menu_view
        elif self.menu_view:
            self.menu.focus_position = "body"
            if _input == "down":
                self.menu.focus_position = "body"
            elif _input == "up":
                self.focus_position = "body"
            elif _input == "right":
                # self.menu.focus_position = "footer"
                self.menu.footer.focus_next() 
            elif _input == "left":
                # self.menu.focus_position = "footer"
                self.menu.footer.focus_previous() 
        # elif _input in (f"ctrl {i}" for i in range(1, len(self.mind.master.players) + 1)):
        #     try:
        #         self.header.focus_position = int(_input)-1 
        #     except:
        #         pass
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
        self.inventory = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        super(InventoryFrame, self).__init__(parent, mind, self.inventory)
        self.state = "normal"

    def on_update(self):
        def show_item(item, button):
            self.state = item.id
        
        def back(button):
            self.state = "normal"
            
        def drop_item(item, button):
            self.player.actions["drop"].use(self.player, obj=item)
            
        # def send_equip(item, button):
        #     if not item.is_equipped:
        #         self.player.equip(item)
            
        # def send_unequip(item, button):
        #     if item.is_equipped:
        #         self.player.unequip(item)
        
        
        widgets = []
        items = [i for i in self.player.inventory.all]
        if self.state == "normal":
            for i in items:   
                line = []            
                btn = create_button(i.name, show_item, attr=i.rarity, user_args = [i])
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
                line.append((6, bdrop))
                if i.is_consumable:
                    btn = create_button("Use", lambda obj=i:obj.on_use)  
                    line.append((6, btn))

                if i.is_equipment:
                    description = urwid.Text(f"- {i.eq_description}")
                else:
                    description = urwid.Text(f"- {i.description}")
                line.append((32, description))
                
                columns = SelectableColumns(line, dividechars=2)
                try:
                    index = self.inventory.focus_position
                    columns.focus_position = self.inventory.body[:][index].focus_position
                except:
                    pass
                
                widgets.append(columns)
        else:
            i = next((it for it in items if it.id == self.state), None)
            if i == None:
                self.state = "normal"
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
        self.state = "normal"

    def on_update(self):
        def open_equipment(typ, button):
            self.state = typ
            
        def send_equip(item, button):
            if not item.is_equipped:
                self.player.equip(item, self.state)
            self.state = "normal"
            
        def send_unequip(button):
            if self.state in self.player.equipment and self.player.equipment[self.state]:
                self.player.unequip(self.state)
            self.state = "normal"
             
        widgets = []
        
        if self.state == "normal":
            t = urwid.Text("", align='center')
            widgets.append(t)
            
            for part, eqp in self.player.equipment.items():
                equip_btn = create_button(f"{' '.join(part.split('_'))}", open_equipment, user_args = [part])
                    
                if eqp:
                    text = urwid.Text([(eqp.rarity, "{} ".format(eqp.name)), eqp.eq_description])
                else:
                    text = urwid.Text("None")
                line = [(16, equip_btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)    
                    
        else:
            t = urwid.Text(f"{' '.join(self.state.split('_'))}", align='center')
            widgets.append(t)
            unequip_btn = create_button("None", send_unequip)
            text = urwid.Text("")
            line = [(16, unequip_btn), text]
            columns = SelectableColumns(line, dividechars=2)
            widgets.append(columns)
            eqs = [i for i in self.player.inventory.all if self.state in i.type  and i.requisites(self.player)]
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
        #self.columns = FrameColumns(self.box, screen_btns)
        super().__init__(parent, mind, box)
        

    def on_update(self):
        # index = self.parent.header_widget.focus_position
        # player = self.header_list[index] #keep this in change we allow to change focus later on
        player= self.player
        _top = f" {player.name:<20s} {player.game_class.name:>12s} Lev:{player.level:<2d} Exp:{player.exp:<6d} {player.location.name} {player.position}\n"

        _left = []
        _left.append(f"╭──────────────────────╮\n")

        for s in ["STR", "INT", "WIS", "CON", "DEX", "CHA"]:
            c = getattr(player, s)
            state = ["normal", "positive", "negative"][-int(c.bonus < 0) + int(c.bonus > 0)]
            _left += [f"│ {c.name:<12} ", (state, f"{c.value:>2d}"), f" ({c.mod:<+2d}) │\n"]
        
        _left.append(f"╰──────────────────────╯\n")
        _left.append(f"╭──────────────────────╮\n")
        _left.append(f"│ Dmg reduction   {player.dmg_reduction:>2d}   │\n")
        _left.append(f"╰──────────────────────╯\n")
        

        _right = []
        _right.append(f"tab: Open/close menu\n")
        _right.append(f"←→↑↓: Move/navigate menu\n")
        _right.append(f"⇦⇨⇧⇩: Dash\n")
        _right.append(f"ctrl+p: Respawn\n")
        _right.append(f"a: attack\n")
        _right.append(f"q: pickup item\n")
        for k, act in player.input_map.items():
            if act in player.class_actions:
                _right.append(f"{k}: {player.class_actions[act].description}\n")
        _right.append("\n\n")
        for k, count in player.counters.items():
            _right.append(f"{k}: {count.value}\n")

        self.box[:] = [urwid.Text(_top), urwid.Columns([urwid.Text(_left), urwid.Text(_right)], dividechars = 1) ]
       
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
            
class InventorySelectableColumns(urwid.Columns):
    def __init__(self, widget_list, index, dividechars=0):
        super(InventorySelectableColumns, self).__init__(widget_list, dividechars)
        self.index = InventorySelectableColumns
    def focus_next(self):
        try: 
            self.focus_position += 1 
            self.index += 1
        except:
            pass
    def focus_previous(self):
        try: 
            self.focus_position -= 1
            self.index = 1
        except:
            pass   

class SelectableColumns(urwid.Columns):
    def __init__(self, widget_list, dividechars=0):
        super(SelectableColumns, self).__init__(widget_list, dividechars)

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

def create_button(label, cmd, attr=None, focus_map = "line", align = "center", user_args = None):
    btn = urwid.Button(label)
    btn._label.align = align
    if user_args:
        urwid.connect_signal(btn, "click", cmd, user_args = user_args)
    else:
        urwid.connect_signal(btn, "click", cmd)
    if attr or focus_map:
        return urwid.AttrMap(btn, attr, focus_map=focus_map)
    return btn
