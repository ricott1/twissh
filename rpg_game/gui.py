# encoding: utf-8

import urwid
import time, os
from collections import OrderedDict
from rpg_game.utils import log, mod
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
            ("reversed", "standout", ""),
            ("common","white","black"),
            ("uncommon","light blue","black"),
            ("rare","yellow","black"),
            ("unique","light magenta","black"),
            ("set","light green","black"),
            ]
HEALTH_BARS_LENGTH = RECOIL_BARS_LENGTH = 15

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

    def focus_next(self):
        pass

    def focus_previous(self):
        pass

    def update_body(self, title, no_title=False):
        self.active_body = self.bodies[title]
        if no_title:
            self.contents["body"] = (urwid.LineBox(self.active_body), None)
        else:
            self.contents["body"] = (urwid.LineBox(self.active_body, title=title), None)

class GUI(UiFrame):
    def __init__(self, parent, mind):
        self.active_body = GameFrame(self, mind)
        super().__init__(parent, mind, self.active_body)

    def on_update(self):
        self.active_body.on_update()
    
    def handle_input(self, _input):
        self.active_body.handle_input(_input)
    
    def exit(self):
        self.disconnect()
        self.mind.disconnect()#should use dispatch event
  

class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        header = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Status", "Map", "Inventory", "Equipment", "Chat")}
        self.active_body = self.bodies["Status"]
        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        footer = FrameColumns(self, screen_btns)

        super().__init__(parent, mind, urwid.LineBox(self.active_body, title="Status"), header=urwid.LineBox(urwid.BoxAdapter(header, HEADER_HEIGHT()), title="Players"),  footer = footer, focus_part="header")
        self.header_widget = self.header.original_widget.box_widget

    def on_update(self):
        self.update_header()
        self.active_body.on_update()     
    
    def handle_input(self, _input):
        # if _input == "down" and self.focus_position == "body":
        #     self.focus_position = "footer"
        # elif _input == "up" and self.focus_position == "body":
        #     self.focus_position = "header"
        # elif (_input == "up" and self.focus_position == "footer") or (_input == "down" and self.focus_position == "header"):
        #     self.focus_position = "body"
        # elif _input == "right":
        #     if self.focus_position == "header":
        #         self.header_widget.focus_next() 
        #     elif self.focus_position == "body":
        #         self.active_body.focus_next() 
        #     elif self.focus_position == "footer":
        #         self.footer.focus_next() 
        # elif _input == "left":
        #     if self.focus_position == "header":
        #         self.header_widget.focus_previous()
        #     elif self.focus_position == "body":
        #         self.active_body.focus_previous() 
        #     elif self.focus_position == "footer":
        #         self.footer.focus_previous()
        if _input == "down":
            self.focus_position = "header"
            self.header_widget.focus_previous() 
        elif _input == "up":
            self.focus_position = "header"
            self.header_widget.focus_next()
        elif _input == "right":
            self.focus_position = "footer"
            self.footer.focus_next() 
        elif _input == "left":
            self.focus_position = "footer"
            self.footer.focus_previous() 
        elif _input in (f"ctrl {i}" for i in range(1, len(self.mind.master.players) + 1)):
            try:
                self.header.focus_position = int(_input)-1 
            except:
                pass
        else:
            self.focus_position = "body"
            self.active_body.handle_input(_input)
       
    def update_header(self):
        player_list = [p for i , p in self.parent.mind.master.players.items()]
        widgets = [urwid.AttrMap(urwid.Text(print_status(p)), None, "line") for p in player_list]
        if widgets:
            self.header_widget.body[:] = widgets
              
class RoomFrame(UiFrame):    
    def __init__(self, parent, mind):
        room = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.room = room.body
        super().__init__(parent, mind, room)
        
    def on_update(self):
        widgets = []
        try:
            index = self.active_body.focus_position
            button_line.focus_position = self.active_body.body[:][index].focus_position
        except:
            pass

        # villains = [c for c in self.player.location.characters if c.__class__.__name__ =="Villain"]
        # for v in villains:
        #     widgets.append(urwid.AttrMap(urwid.Text(print_status(v)),None,"line"))

        self.room[:] = widgets

class MapFrame(UiFrame):    
    def __init__(self, parent, mind):
        map_box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.map_box = map_box.body
        super().__init__(parent, mind, map_box)
        
    def on_update(self):
        _map = self.player.location.map
        x, y, z = self.player.position
        widget_height = SIZE()[1] - HEADER_HEIGHT() - FOOTER_HEIGHT - 2
        visible_map = [line for j, line in enumerate(_map) if abs(x-j)<widget_height//2]
        
        #color player cursor
        visible_map[x][y] = ("player", self.player.marker)

        # #color (other) active player cursor
        # index = self.parent.header_widget.focus_position
        # players = [p for i, p in self.mind.master.players.items()]
        # active_player = players[index]
        # if active_player != self.player:
        #     xp, yp, zp = active_player.position
        #     visible_map[yp][xp] = ("other", active_player.marker)

        self.map_box[:] = [urwid.Text(line) for line in visible_map]

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
            self.player.drop(obj=item)
            
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
                line.append((22, btn))
                if i.is_equipment:
                    description = urwid.Text((" - {} {}".format(i.eq_description, "(eq)"*int(i.is_equipped))))
                else:
                    description = urwid.Text()
                line.append((38, description))
                
                
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
                if i.is_consumable:
                    btn = create_button("Use", lambda obj=i:obj.on_use)  
                    line.append((18, btn))   
                bdrop = create_button("Drop", drop_item, user_args = [i])
                line.append((12, bdrop))
                
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
                name = urwid.Text((i.rarity, i.name))
                widgets.append(name)
                widgets.append(urwid.Text("Rarity: {}".format(i.rarity)))
                if i.is_equipment:
                    description = urwid.Text((" - {} {}".format(i.eq_description, "(eq)"*int(i.is_equipped))))
                else:
                    description = urwid.Text()
                widgets.append(description)
                for d in i.description:
                    widgets.append(urwid.Text(d))
                
                bback =  create_button("Back", back)
                
                widgets.append(SelectableColumns([(8, bback)]))       
        self.body.body[:] = widgets

    def handle_input(self, _input):
        if _input == "w":
            self.body.focus_previous() 
        elif _input == "s":
            self.body.focus_next()

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
            t = urwid.Text("{}".format(self.state), align='center')
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

    def handle_input(self, _input):
        if _input == "w":
            self.body.focus_previous() 
        elif _input == "s":
            self.body.focus_next()

class StatusFrame(UiFrame):    
    def __init__(self, parent, mind):
        box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.box = box.body
        #self.columns = FrameColumns(self.box, screen_btns)
        super().__init__(parent, mind, box)
        

    def on_update(self):
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.mind.master.players.items()]
        player = players[index]
        
        data = []
        data.append(f" {player.name:<20s} Lev:{player.level:<2d} Exp:{player.exp:<6d} {player.location.name}\n")
        data.append(f"╭──────────────────────╮")
        data.append(f"│ Strength     {player.str:>2d} ({player.STR.mod:<+2d}) │")
        data.append(f"│ Intelligence {player.int:>2d} ({player.INT.mod:<+2d}) │")
        data.append(f"│ Wisdom       {player.wis:>2d} ({player.WIS.mod:<+2d}) │")
        data.append(f"│ Constitution {player.con:>2d} ({player.CON.mod:<+2d}) │")
        data.append(f"│ Dexterity    {player.dex:>2d} ({player.DEX.mod:<+2d}) │")
        data.append(f"│ Charisma     {player.cha:>2d} ({player.CHA.mod:<+2d}) │")
        data.append(f"╰──────────────────────╯")

        
        data.append(f"╭──────────────────────╮")
        data.append(f"│ Dmg reduction   {player.dmg_reduction:>2d}   │")
        data.append(f"╰──────────────────────╯")
        
        widgets = [urwid.Text(d) for d in data]
        self.box[:] = widgets
       
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
                self.player.chat_sent_log.append({"sender":self.player.name, "time":time.time(), "text":text})

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

def print_status(char):
        #"➶""⚝""✨""⚔"❂✮ ⚝
                
        if char.is_dead:
            h = u"☠"
        #elif char.is_dreaming:
        #     h = u"☾"
        # elif char.is_shocked:
        #     h = u"⚡"
        # elif char.is_muted:
        #     h = u"∅"
        #elif char.on_rythm==1:
        #    h = u"✨"
        #elif char.on_rythm==2:
        #    h = u"✨"
        elif char.hp < char.HP.max: 
            h = u"♡"
        elif char.hp == char.HP.max: 
            h = u"♥" 

        health_bars = int(round(char.hp/char.HP.max * HEALTH_BARS_LENGTH))
        recoil_bars = int(round((char.recoil)/MAX_RECOIL  * RECOIL_BARS_LENGTH))
        hp = health_bars * u"\u25B0" + (HEALTH_BARS_LENGTH - health_bars) * u"\u25B1"
        recoil = (RECOIL_BARS_LENGTH - recoil_bars) * u"\u25AE" + recoil_bars * u"\u25AF" 
#{int(char.recoil):2d}
        if SIZE()[0] >= 80:
            return  f"{char.name:16s} {hp}{h} {char.hp:>4d}/{char.HP.max:<4d} {recoil}: {char.print_action:20s}"
        return  f"{char.name:16s} {h}{hp} {char.hp:>4d}/{char.HP.max:<4d}\n{recoil}: {char.print_action:20s}"

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
