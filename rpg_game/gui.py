# encoding: utf-8

import urwid
import time, os
from collections import OrderedDict

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
BREATH_BARS_LENGTH = STAMINA_BARS_LENGTH = RECOIL_BARS_LENGTH = 15

class UiFrame(urwid.Frame):
    def __init__(self, parent, mind, *args, **kargs):
        self.parent = parent 
        self.mind = mind
        urwid.AttrMap(self,"frame")
        super(UiFrame, self).__init__(*args, **kargs)

    def handle_input(self, input):
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

class GUI(UiFrame):#convert to UIFrame?
    def __init__(self, parent, mind):
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Game", "Start", "Create", "Help")}

        self.active_body = self.bodies["Start"]
        super(GUI, self).__init__(parent, mind, self.active_body)

    def on_update(self):
        self.active_body.on_update()
    
    def handle_input(self, input):
        self.active_body.handle_input(input)
    
    def exit(self):
        self.disconnect()
        self.mind.disconnect()#should use dispatch event
  
class StartFrame(UiFrame):
    def __init__(self, parent, mind):
        body = [urwid.Divider()]

        body.append(create_button("New Game", self.new_game))
        body.append(create_button("Quick Start", self.quick_game,))
        body.append(create_button("Help", self.help))
        body.append(create_button("Quit", self.exit))
        
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        overlay = urwid.Overlay(listbox, urwid.SolidFill(u"\N{MEDIUM SHADE}"),
            align="center", width=("relative", 60),
            valign="middle", height=("relative", 60),
            min_width=40, min_height=16)
        super(StartFrame, self).__init__(parent, mind, overlay)
     
    def new_game(self, button):
        self.parent.update_body("Create", no_title=True)
        
    def quick_game(self, button):
        self.parent.mind.master.quick_game(self.parent.mind.avatar.uuid)
        self.parent.update_body("Game", no_title=True)
            
    def help(self, button):
        self.parent.update_body("Help")  

    def exit(self, button):
        self.parent.exit()
                
class CreateFrame(UiFrame):
    def __init__(self, parent, mind):
        #list: base value, min value, max value, increment, cost
        self.temp_chars = OrderedDict([("HP", [8, 4, 12, 2, 1]), ("HB", [60, 40, 80, -3, 1]), ("MP", [6, 4, 18, 1, 1]), ("STR", [6, 4, 18, 1, 1]), ("RES", [6, 4, 18, 1, 1]), ("SPD", [6, 4, 18, 1, 1]), 
        ("DEX", [6, 4, 18, 1, 1]), ("MAG", [6, 4, 18, 1, 1]), ("RTM", [1, 1, 3, 1, 2])])
        self.temp_text = {key: urwid.Text(str(self.temp_chars[key][0])) for key in self.temp_chars }
        self.points = 40
        self.points_text = urwid.Text("Points: {}".format(self.points))
        self.name_edit = urwid.Edit("Name: ")
        body = [urwid.Text("Create a new character"), urwid.Divider(), self.name_edit, self.points_text]
        
        
        for c in self.temp_chars:
            b_plus = create_button("+", self.update_char, user_args = [c, +1])
            b_minus = create_button("-", self.update_char, user_args = [c, -1])
            columns = [(3, urwid.Text(c)), (2, self.temp_text[c]), (1, b_minus), (1, b_plus)]
            
            line = urwid.Columns(columns, dividechars=1, focus_column=3, min_width=1, box_columns=None)
            body.append(line)
        
        body.append(urwid.Divider())
        body.append(create_button("Start", self.start))
        body.append(create_button("Back", self.back))
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        overlay = urwid.Overlay(listbox, urwid.SolidFill(u"\N{MEDIUM SHADE}"),
            align="center", width=("relative", 60),
            valign="middle", height=("relative", 60),
            min_width=40, min_height=16)
        super(CreateFrame, self).__init__(parent, mind, overlay)
            
     
    def update_char(self, char, value, button):
        if (self.temp_chars[char][2]>=self.temp_chars[char][0] + value * self.temp_chars[char][3]>= self.temp_chars[char][1]) and self.points - value * self.temp_chars[char][4]>=0:
            self.points -= value * self.temp_chars[char][4]
            self.temp_chars[char][0] += value * self.temp_chars[char][3]
            self.temp_text[char].set_text(str(self.temp_chars[char][0]))
            self.points_text.set_text("Points: {}".format(self.points))

    def start(self, button):
        data = {key: self.temp_chars[key][0] for key in self.temp_chars }
        data["name"] = self.name_edit.get_edit_text()[:12]
        self.parent.mind.master.create_player(self.parent.mind.avatar.uuid, data)
        self.parent.update_body("Game")

    def back(self, button):
        self.parent.update_body("Start")
        
class HelpFrame(UiFrame):
    def __init__(self, parent, mind):
        text = """
 write me, help!
 help!"""
        utext = urwid.Text(text, align="left")
        
        body = [utext]
       
        back_button = urwid.Button("Back")
        back_button._label.align = "center"
        urwid.connect_signal(back_button, "click", self.back)
        body.append(urwid.AttrMap(back_button, None, focus_map="line"))
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        overlay = urwid.Overlay(listbox, urwid.SolidFill(u"\N{MEDIUM SHADE}"),
            align="center", width=("relative", 60),
            valign="middle", height=("relative", 60),
            min_width=40, min_height=16)
        super(HelpFrame, self).__init__(parent, mind, overlay)
            
    def back(self, button):
        self.parent.update_body("Start")           
    
class GameFrame(UiFrame):
    def __init__(self, parent, mind):
        header = SelectableListBox(urwid.SimpleListWalker([urwid.Text("")]))
        
        self.bodies = {b : globals()[f"{b}Frame"](self, mind) for b in ("Status", "Room", "Inventory", "Equipment", "Map", "Chat")}
        self.active_body = self.bodies["Status"]
        screen_btns = [urwid.LineBox(urwid.AttrMap(urwid.Text("{:^10}".format(s), align="center"), None, focus_map="line")) for s in self.bodies]
        footer = FrameColumns(self, screen_btns)

        super(GameFrame, self).__init__(parent, mind, urwid.LineBox(self.active_body, title="Status"), header=urwid.LineBox(urwid.BoxAdapter(header, 12), title="Players"),  footer = footer, focus_part="header")
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
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.mind.master.players.items()]
        player = players[index]
        loots = ["Lootings: "] + [(loot.rarity, "{} ".format(loot.name)) for loot in player.location.inventory] 
        widgets = [urwid.Text(loots)]
        try:
            index = self.active_body.focus_position
            button_line.focus_position = self.active_body.body[:][index].focus_position
        except:
            pass

        villains = [c for c in player.location.characters if c.__class__.__name__ =="Villain"]
        for v in villains:
            widgets.append(urwid.AttrMap(urwid.Text(print_status(v)),None,"line"))

        self.room[:] = widgets

class MapFrame(UiFrame):    
    def __init__(self, parent, mind):
        map_box = urwid.ListBox(urwid.SimpleListWalker([urwid.Text("")]))
        self.map_box = map_box.body
        super(MapFrame, self).__init__(parent, mind, map_box)
        
    def on_update(self):
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.mind.master.players.items()]
        player = players[index]
        
        
        x, y = player.position
        vis = player.location.visible_map
        # line = ws[y]
        # ws[y] = urwid.Text([ws[y][:x], ("other", player.marker), ws[y][x + 1:]])
        self.map_box[:] = [urwid.Text(line)  if y != j else  urwid.Text([line[:x], ("other", player.marker), line[x + 1:]]) for j, line in enumerate(vis)]

    def handle_input(self, input):
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.mind.master.players.items()]
        player = players[index]
        if input == "w":
            player.move("up")
        elif input == "s":
            player.move("down")
        elif input == "a":
            player.move("left")
        elif input == "d":
            player.move("right")


class InventoryFrame(UiFrame):    
    def __init__(self, parent, mind):
        super(InventoryFrame, self).__init__(parent, mind, SelectableListBox(urwid.SimpleListWalker([urwid.Text("")])))
        self.state = "normal"

    def on_update(self):
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.parent.parent.mind.master.players.items()]
        player = players[index]
        def show_item(item, button):
            self.state = item.id
        
        def back(button):
            self.state = "normal"
            
        def drop_item(item, button):
            player.drop(item)
            
        def send_equip(item, button):
            if not item.is_equipped:
                player.equip(item)
            
        def send_unequip(item, button):
            if item.is_equipped:
                player.unequip(item)
        
        widgets = []
        items = [i for i in player.inventory]
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
                    if i.requisites(player):
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
                    index = self.active_body.focus_position
                    columns.focus_position = self.active_body.body[:][index].focus_position
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
        index = self.parent.header_widget.focus_position
        players = [p for i, p in self.parent.parent.mind.master.players.items()]
        player = players[index]
        def open_equipment(typ, button):
            self.state = typ
            
        def send_equip(item, button):
            if not item.is_equipped:
                player.equip(item)
            self.state = "normal"
            
        def send_unequip(button):
            if self.state in player.equipment:
                player.unequip(player.equipment[self.state])
            self.state = "normal"
             
        widgets = []
        
        if self.state == "normal":
            t = urwid.Text("", align='center')
            widgets.append(t)
            
            for e in ["Weapon", "Armor", "Helm", "Belt", "Gloves", "Boots"]:
                equip_btn = create_button(f"{e}", open_equipment, user_args = [e])
                    
                if e in player.equipment:
                    i = player.equipment[e]
                    bonus = ",".join([" {}: {} ".format(bns, i.bonus[bns]) for bns in i.bonus if i.bonus[bns]!=0])
                    text = urwid.Text([(i.rarity, "{} ".format(i.name)), bonus])
                else:
                    text = urwid.Text("None")
                line = [(16, equip_btn), text]
                columns = SelectableColumns(line, dividechars=2)
                widgets.append(columns)    
                    
            bonus = player.bonus.copy()            
            for obj in player.equipment:
                for b in player.equipment[obj].bonus:
                    if b in bonus:
                        bonus[b] += player.equipment[obj].bonus[b]
                    
            t.set_text(" ".join(["{:3}: {:<2}".format(b, bonus[b]) for b in bonus]))
        else:
            t = urwid.Text("{}".format(self.state), align='center')
            widgets.append(t)
            unequip_btn = create_button("None", send_unequip)
            text = urwid.Text("")
            line = [(16, unequip_btn), text]
            columns = SelectableColumns(line, dividechars=2)
            widgets.append(columns)
            eqs = [i for i in player.inventory if i.type == self.state and i.requisites(player)]
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
        if player.is_dreaming:
            state += "Dreaming "
        if player.is_muted:
            state += "Muted "
        if player.is_shocked:
            state += "Shocked "
            
        data = """
        {:>10s} {:<10s} Lev:{:2d} Exp:{:<6d} {}
            MP:{:>3d}/{:<3d} HB:{:<3d}/{:<3d}  HP:{:<11s} RTM:{:>1d}/{:<3d} AC:{:<3d}
            STR:{:<2d}({:+d})  RES:{:<2d}({:+d})  MAG:{:<2d}({:+d})  SPD:{:<2d}({:+d})  DEX:{:<2d}({:+d})
            Room: {}""".format(player.race.name, player.job.name, player.level, player.exp, state,
                    player.MP, player.max_MP, player.HB, player.max_HB, str(int(player.STA)) +"/"+str(player.HP)+"/"+str(player.max_HP), player.on_rythm, player.RTM, player.AC,
                    player.STR, player.STRmod, player.RES, player.RESmod, player.MAG, player.MAGmod, player.SPD, player.SPDmod, player.DEX, player.DEXmod,          
                    player.location.name)
        
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
        elif char.is_dreaming:
            h = u"☾"
        elif char.is_shocked:
            h = u"⚡"
        elif char.is_muted:
            h = u"∅"
        #elif char.on_rythm==1:
        #    h = u"✨"
        #elif char.on_rythm==2:
        #    h = u"✨"
        else: 
            h = [u"♡",u"♥"][int(time.time())%2] 
        
        if char.is_catching_breath >0:        
            breath = "Breathing "
            breath_bars = int( round((1.-char.is_catching_breath/char.time_to_catch_breath()) * BREATH_BARS_LENGTH))
            
        elif char.MP >= 0:
            b = "Breath" if not char.on_rythm else "Rythm "
            breath = "{:<6s}:{:<3d}".format(b, char.MP)
            breath_bars = int(round(1.*char.MP/char.max_MP * BREATH_BARS_LENGTH))
        stamina = " {:>d}/{:^d}/{:<d} ".format(int(round(char.STA)), char.HP, char.max_HP)
        stamina_bars = int(round(1.*char.STA/(char.max_HP) * STAMINA_BARS_LENGTH))
        max_stamina_bars = int(round(1.*char.HP/(char.max_HP) * STAMINA_BARS_LENGTH))
        max_bars = STAMINA_BARS_LENGTH
        recoil_bars = int(round((100. - char.recoil)/100  * RECOIL_BARS_LENGTH))
        max_recoil_bars = RECOIL_BARS_LENGTH
        incipit = f"{char.name}, {char.race.name} {char.job.name} {char.job.level}"
        return u"""
            {:12s} {:1s} {:<3d} {:^17s} {:^18s}   
            {:16s}   {:17s} {:18s} {}""".format(incipit, h, char.HB, stamina, breath,
            recoil_bars * u"\u25AE" + (max_recoil_bars - recoil_bars) * u"\u25AF", stamina_bars * u"\u25B0" + (max_stamina_bars - stamina_bars) * u"\u25B1"+' '*(max_bars-max_stamina_bars)+'/', ":" + breath_bars* "|" + ' '*(max_bars - breath_bars) + ":",  char.print_action)

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
        
def log(text):
    with open("log.tiac", "a") as f:
        f.write("{}: {}\n".format(time.time(), text))


