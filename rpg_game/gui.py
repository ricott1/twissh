# encoding: utf-8

import urwid
import time, os
from collections import OrderedDict
from rpg_game.utils import log, mod
from urwid import raw_display

SIZE = lambda scr=raw_display.Screen(): scr.get_cols_rows()
HEADER_HEIGHT = 12
FOOTER_HEIGHT = 5

PALETTE = [
            ("line", 'black', 'white', "standout"),
            ("top","white","black"),
            ("frame","white","white"),
            ("player", "light green", ""),
            ("other", "light blue", ""),
            ("reversed", "standout", ""),
            ("common","white",""),
            ("uncommon","light blue",""),
            ("rare","yellow",""),
            ("unique","light magenta",""),
            ("set","light green",""),
            ]
HEALTH_BARS_LENGTH = RECOIL_BARS_LENGTH = 15

class UiFrame(urwid.Frame):
    def __init__(self, parent, mind, *args, **kargs):
        self.parent = parent 
        self.mind = mind
        urwid.AttrMap(self,"frame")
        super(UiFrame, self).__init__(*args, **kargs)

    @property
    def player(self):
        if self.mind.avatar.uuid in self.mind.master.players:
            return self.mind.master.players[self.mind.avatar.uuid]
        else: 
            return None

    def handle_input(self, input):
        pass

    def on_update(self):
        passg

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
        super(GUI, self).__init__(parent, mind, self.active_body)
        self.mind.master.quick_game(self.mind.avatar.uuid)

    def on_update(self):
        self.active_body.on_update()
    
    def handle_input(self, input):
        self.active_body.handle_input(input)
    
    def exit(self):
        self.disconnect()
        self.mind.disconnect()#should use dispatch event
  

class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        header = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Status", "Room", "Inventory", "Equipment", "Map", "Chat")}
        self.active_body = self.bodies["Status"]
        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        footer = FrameColumns(self, screen_btns)

        super(GameFrame, self).__init__(parent, mind, urwid.LineBox(self.active_body, title="Status"), header=urwid.LineBox(urwid.BoxAdapter(header, HEADER_HEIGHT), title="Players"),  footer = footer, focus_part="header")
        self.header_widget = self.header.original_widget.box_widget

    def on_update(self):
        self.update_header()
        self.active_body.on_update()     
    
    def handle_input(self, input):
        if input == "down" and self.focus_position == "body":
            self.focus_position = "footer"
        elif input == "up" and self.focus_position == "body":
            self.focus_position = "header"
        elif (input == "up" and self.focus_position == "footer") or (input == "down" and self.focus_position == "header"):
            self.focus_position = "body"
        elif input == "right":
            if self.focus_position == "header":
                self.header_widget.focus_next() 
            elif self.focus_position == "body":
                self.active_body.focus_next() 
            elif self.focus_position == "footer":
                self.footer.focus_next() 
        elif input == "left":
            if self.focus_position == "header":
                self.header_widget.focus_previous()
            elif self.focus_position == "body":
                self.active_body.focus_previous() 
            elif self.focus_position == "footer":
                self.footer.focus_previous()
        # elif input in [f"ctrl {s["key_binding"]}" for s in self.bodies]:
        #     self.footer.focus_position = 0  
        
        elif input in (f"ctrl {i}" for i in range(1, len(self.parent.mind.master.players) + 1)):
            try:
                self.header.focus_position = int(input)-1 
            except:
                pass
        else:
            self.active_body.handle_input(input)
       
    def update_header(self):
        player_list = [p for i , p in self.parent.mind.master.players.items()]
        widgets = [urwid.AttrMap(urwid.Text(print_status(p)), None, "line") for p in player_list]
        if widgets:
            self.header_widget.body[:] = widgets
              
class RoomFrame(UiFrame):    
    def __init__(self, parent, mind):
        room = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.room = room.body
        super(RoomFrame, self).__init__(parent, mind, room)
        
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
        super(MapFrame, self).__init__(parent, mind, map_box)
        
    def on_update(self):
        vis = self.player.location.map
        x, y = self.player.position
        widget_height = SIZE()[1] - HEADER_HEIGHT - FOOTER_HEIGHT - 2
        self.map_box[:] = [urwid.Text(line)  for j, line in enumerate(vis) if abs(y-j)<widget_height//2]

    def handle_input(self, input):
        if input == "w":
            self.player.move("up")
        elif input == "s":
            self.player.move("down")
        elif input == "a":
            self.player.move("left")
        elif input == "d":
            self.player.move("right")
        elif input == "p":
            self.player.pickup()

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
            self.player.drop(item)
            
        def send_equip(item, button):
            if not item.is_equipped:
                self.player.equip(item)
            
        def send_unequip(item, button):
            if item.is_equipped:
                self.player.unequip(item)
        
        widgets = []
        items = [i for i in self.player.inventory]
        if self.state == "normal":
            for i in items:
                bonus = ",".join([" {}: {} ".format(bns, i.bonus[bns]) for bns in i.bonus if i.bonus[bns]!=0] ) + " " + ",".join([" {}: {} ".format(ab, i.abilities[ab].name) for ab in i.abilities] )
               
                bname = urwid.Button(i.name)
                bname._label.align = 'center'
                name_button = urwid.AttrMap(bname,i.rarity,"line")
                urwid.connect_signal(bname, "click", show_item, user_args = [i])
                bonus_text = urwid.Text((" - {} {}".format(bonus, "(eq)"*int(i.is_equipped))))
                bdrop = urwid.Button("Drop") 
                bdrop._label.align = 'center'
                urwid.connect_signal(bdrop, "click", drop_item, user_args = [i])
                if i.is_equipment:
                    if i.requisites(self.player):
                        if i.is_equipped:
                            bequip = urwid.Button("Unequip") 
                            bequip._label.align = 'center'
                            urwid.connect_signal(bequip, "click", send_unequip, user_args = [i])
                        elif not i.is_equipped:
                            bequip = urwid.Button("Equip") 
                            bequip._label.align = 'center'
                            urwid.connect_signal(bequip, "click", send_equip, user_args = [i])
                    else:
                        bequip = urwid.Button("Not Equipable") 
                        bequip._label.align = 'center'                
                else:
                    bequip = urwid.Button("Use") 
                    bequip._label.align = 'center'     
                line = [(22, name_button), (38, bonus_text), (18, urwid.AttrMap(bequip,None,"line")),(12, urwid.AttrMap(bdrop,None,"line"))]
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
                bonus = ",".join([" {}: {} ".format(bns, i.bonus[bns]) for bns in i.bonus if i.bonus[bns]!=0] ) + " " + ",".join([" {}: {} ".format(ab, i.abilities[ab].name) for ab in i.abilities] )
                bonus_text = urwid.Text(("{}".format(bonus)))
                widgets.append(bonus_text)
                for d in i.description:
                    widgets.append(urwid.Text(d))
                
                bback =  create_button("Back", back)
                
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
                self.player.equip(item)
            self.state = "normal"
            
        def send_unequip(button):
            if self.state in self.player.equipment:
                self.player.unequip(player.equipment[self.state])
            self.state = "normal"
             
        widgets = []
        
        if self.state == "normal":
            t = urwid.Text("", align='center')
            widgets.append(t)
            
            for e in ["Weapon", "Armor", "Helm", "Belt", "Gloves", "Boots"]:
                equip_btn = create_button(f"{e}", open_equipment, user_args = [e])
                    
                if e in self.player.equipment:
                    i = self.player.equipment[e]
                    bonus = ",".join([" {}: {} ".format(bns, i.bonus[bns]) for bns in i.bonus if i.bonus[bns]!=0])
                    text = urwid.Text([(i.rarity, "{} ".format(i.name)), bonus])
                else:
                    text = urwid.Text("None")
                line = [(16, equip_btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)    
                    
            bonus = self.player.bonus.copy()            
            for obj in self.player.equipment:
                for b in self.player.equipment[obj].bonus:
                    if b in bonus:
                        bonus[b] += self.player.equipment[obj].bonus[b]
                    
            t.set_text(" ".join(["{:3}: {:<2}".format(b, bonus[b]) for b in bonus]))
        else:
            t = urwid.Text("{}".format(self.state), align='center')
            widgets.append(t)
            unequip_btn = create_button("None", send_unequip)
            text = urwid.Text("")
            line = [(16, unequip_btn), text]
            columns = SelectableColumns(line, dividechars=2)
            widgets.append(columns)
            eqs = [i for i in self.player.inventory if i.type == self.state and i.requisites(self.player)]
            for i in eqs:
                bonus = ",".join([" {}: {}".format(bns, i.bonus[bns]) for bns in i.bonus if i.bonus[bns]!=0]) + " " + ",".join([" {}: {} ".format(ab, i.abilities[ab].name) for ab in i.abilities] )
                b = urwid.Button(i.name)
                b._label.align = 'center'
                text = urwid.Text("{} {}".format(bonus, "(eq)"*int(i.is_equipped)))
                w = urwid.AttrMap(b,i.rarity,"line")
                urwid.connect_signal(b, "click", send_equip, user_args = [i])
                line = [(16, w), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)

        self.body.body[:] = widgets

class StatusFrame(UiFrame):    
    def __init__(self, parent, mind):
        super(StatusFrame, self).__init__(parent, mind, SelectableListBox(urwid.SimpleListWalker([urwid.Text("")])))

    def on_update(self):
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.parent.parent.mind.master.players.items()]
        player = players[index]
        state = ''
        if player.is_dead:
            state += "Dead "
            
        data = ""
        # {:>10s} {:<10s} Lev:{:2d} Exp:{:<6d} {}
        #     MP:{:>3d}/{:<3d} HB:{:<3d}/{:<3d}  HP:{:<11s} WIS:{:>1d}/{:<3d} AC:{:<3d}
        #     STR:{:<2d}({:+d})  CON:{:<2d}({:+d})  INT:{:<2d}({:+d})  CHA:{:<2d}({:+d})  DEX:{:<2d}({:+d})
        #     Room: {}""".format(player.race.name, player.job.name, player.level, player.exp, state,
        #             player.MP, player.max_MP, player.HB, player.max_HB, str(int(player.STA)) +"/"+str(player.HP)+"/"+str(player.max_HP), player.on_rythm, player.WIS, player.AC,
        #             player.STR, mod(player.STR), player.CON, mod(player.CON), player.INT, mod(player.INT), player.CHA, mod(player.CHA), player.DEX, mod(player.DEX),          
        #             player.location.name)
        
        widgets = [urwid.Text(data)]
        self.body.body[:] = widgets
       
class ChatFrame(UiFrame):
    def __init__(self, parent, mind):
        
        self.footer = urwid.Edit("> ")

        self.generic_output_walker = urwid.SimpleListWalker([])
        self.body = ExtendedListBox(
            self.generic_output_walker)

        self.footer.set_wrap_mode("space")
        super(ChatFrame, self).__init__(parent, mind, self.body, 
                                 footer=self.footer)
        self.set_focus("footer")

    def on_update(self):
        pass

    def handle_input(self, input):
        """ 
            Handle user inputs
        """

        #urwid.emit_signal(self, "keypress", size, key)

        # scroll the top panel
        if input in ("page up","page down", "shift left", "shift right"):
            self.body.handle_input(input)

        # resize the main windows
        elif input == "window resize":
            self.size = self.ui.get_cols_rows()

        elif input == "enter":
            # Parse data or (if parse failed)
            # send it to the current world
            text = self.footer.get_edit_text()

            self.footer.set_edit_text(" "*len(text))
            self.footer.set_edit_text("")

            if text.strip():
                self.print_sent_message(text)
                self.print_received_message('Answer')

        # else:
        #     self.keypress(input)

    def print_sent_message(self, text):
        self.print_text('You:')
        self.print_text(text)
 
    def print_received_message(self, text):
        header = urwid.Text('System:')
        header.set_align_mode('right')
        self.print_text(header)
        text = urwid.Text(text)
        text.set_align_mode('right')
        self.print_text(text)
        
    def print_text(self, text):
        walker = self.generic_output_walker
        if not isinstance(text, urwid.Text):
            text = urwid.Text(text)
        walker.append(text)
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


    def handle_input(self, input):
        if input == "shift left":
            input = "page up"
        elif input == "shift right":
            input = "page down"
        urwid.ListBox.keypress(self, (80, 24), input)

        if input in ("page up", "page down"):
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
        recoil_bars = int(round((char.recoil)/char.MAX_RECOIL  * RECOIL_BARS_LENGTH))
        hp = health_bars * u"\u25B0" + (HEALTH_BARS_LENGTH - health_bars) * u"\u25B1"
        recoil = recoil_bars * u"\u25AE" + (RECOIL_BARS_LENGTH - recoil_bars) * u"\u25AF"

        if SIZE()[0] >= 80:
            return  f"{char.name:16s} {hp}{h} {char.hp:4d}/{char.HP.max:4d} {recoil}:{char.print_action:20s}"
        return  f"{char.name:16s} {h}{hp} {char.hp:4d}/{char.HP.max:4d}\n{recoil}:{char.print_action:20s}"

def create_button(label, cmd, focus = "line", align = "center", user_args = None):
    btn = urwid.Button(label)
    btn._label.align = align
    if user_args:
        urwid.connect_signal(btn, "click", cmd, user_args = user_args)
    else:
        urwid.connect_signal(btn, "click", cmd)
    if focus:
        return urwid.AttrMap(btn, None, focus_map=focus)
    return btn
