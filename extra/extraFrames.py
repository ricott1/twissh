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
        self.mind.master.quick_game(self.mind.avatar.uuid)
        self.parent.update_body("Game", no_title=True)
            
    def help(self, button):
        self.parent.update_body("Help")  

    def exit(self, button):
        self.parent.exit()
                
class CreateFrame(UiFrame):
    def __init__(self, parent, mind):
        #list: base value, min value, max value, increment, cost
        self.temp_chars = OrderedDict([("HP", [8, 4, 12, 2, 1]), ("HB", [60, 40, 80, -3, 1]), ("MP", [6, 4, 18, 1, 1]), ("STR", [6, 4, 18, 1, 1]), ("CON", [6, 4, 18, 1, 1]), ("CHA", [6, 4, 18, 1, 1]), 
        ("DEX", [6, 4, 18, 1, 1]), ("INT", [6, 4, 18, 1, 1]), ("WIS", [1, 1, 3, 1, 2])])
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
    
